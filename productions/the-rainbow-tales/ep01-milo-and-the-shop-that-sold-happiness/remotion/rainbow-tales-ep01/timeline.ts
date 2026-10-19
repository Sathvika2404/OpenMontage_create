// Evaluates an explicit action timeline (timelines/*.json) into per-frame
// channel values. Deterministic: every frame is a pure function of the JSON.
//
// value(channel, t) = keyframes(channel, t) + Σ oscillators(channel, t) + Σ follow(channel, t)

import { Easing } from "remotion";

export type Ease = "linear" | "in" | "out" | "inOut" | "outBack";
export type Key = [number, number, Ease];

export type Oscillator = {
  channel: string;
  start: number;
  end: number;
  amplitude: number;
  period_seconds: number;
  fade_seconds: number;
  shape: "sine" | "sine_positive";
};

export type Follow = {
  channel: string;
  source: string;
  gain: number;
  stiffness: number;
  damping: number;
};

export type ActionTimeline = {
  id: string;
  fps: number;
  duration_seconds: number;
  channels: Record<string, Key[]>;
  oscillators?: Oscillator[];
  follow?: Follow[];
};

const EASES: Record<Ease, (t: number) => number> = {
  linear: (t) => t,
  in: Easing.in(Easing.cubic),
  out: Easing.out(Easing.cubic),
  inOut: Easing.inOut(Easing.cubic),
  outBack: Easing.out(Easing.back(1.4)),
};

const sampleKeys = (keys: Key[] | undefined, t: number): number => {
  if (!keys || keys.length === 0) return 0;
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [t1, v1, ease] = keys[i];
    if (t <= t1) {
      const [t0, v0] = keys[i - 1];
      const p = t1 === t0 ? 1 : (t - t0) / (t1 - t0);
      return v0 + (v1 - v0) * EASES[ease](p);
    }
  }
  return keys[keys.length - 1][1];
};

const sampleOscillator = (o: Oscillator, t: number): number => {
  if (t < o.start || t > o.end) return 0;
  const phase = ((t - o.start) / o.period_seconds) * Math.PI * 2;
  let env = 1;
  if (o.fade_seconds > 0) {
    env = Math.min(1, (t - o.start) / o.fade_seconds, (o.end - t) / o.fade_seconds);
    env = EASES.inOut(Math.max(0, env));
  }
  const wave = o.shape === "sine_positive" ? (1 - Math.cos(phase)) / 2 : Math.sin(phase);
  return o.amplitude * env * wave;
};

// Base (keys + oscillators) value, used as the input to follow springs.
const baseValue = (tl: ActionTimeline, channel: string, t: number): number => {
  let v = sampleKeys(tl.channels[channel], t);
  for (const o of tl.oscillators ?? []) {
    if (o.channel === channel) v += sampleOscillator(o, t);
  }
  return v;
};

export type Evaluated = (channel: string, frame: number) => number;

// Precomputes spring-follow channels once (damped spring integrated over every
// frame), so evaluation stays O(1) per frame and frame-order independent.
export const compileTimeline = (tl: ActionTimeline): Evaluated => {
  const frames = Math.round(tl.duration_seconds * tl.fps) + 1;
  const dt = 1 / tl.fps;
  const followed: Record<string, Float64Array> = {};
  for (const f of tl.follow ?? []) {
    const out = followed[f.channel] ?? new Float64Array(frames);
    let x = f.gain * baseValue(tl, f.source, 0);
    let vel = 0;
    const substeps = 8;
    for (let i = 0; i < frames; i++) {
      for (let s = 0; s < substeps; s++) {
        const t = (i + s / substeps) * dt;
        const target = f.gain * baseValue(tl, f.source, t);
        const acc = f.stiffness * (target - x) - f.damping * vel;
        vel += acc * (dt / substeps);
        x += vel * (dt / substeps);
      }
      out[i] += x;
    }
    followed[f.channel] = out;
  }
  return (channel, frame) => {
    const t = frame / tl.fps;
    const extra = followed[channel];
    const f = Math.max(0, Math.min(frames - 1, Math.round(frame)));
    return baseValue(tl, channel, t) + (extra ? extra[f] : 0);
  };
};
