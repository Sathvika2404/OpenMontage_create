// Reusable 2.5D front-view puppet for Milo, driven by rig JSON + a pose.
// All layers share one canvas (rig.canvas), so each layer is a full-canvas
// image transformed around its pivot. Character differences live in the rig
// data, not in this component.

import React from "react";
import { Img, staticFile } from "remotion";

type Vec = [number, number];
type EyeGeom = { cx: number; cy: number; rx: number; ry: number };

export type MiloRig = {
  canvas: { width: number; height: number };
  pivots: Record<string, Vec>;
  eyes: { left: EyeGeom; right: EyeGeom };
  limits_px?: { head_offset: number };
  eyelid: { mode: string; half_full_at: number; closed_from: number; closed_full_at: number };
  limits_deg: Record<string, [number, number]>;
  layers: Record<string, { file: string }>;
};

export type MiloPose = {
  breath: number; // fractional vertical stretch of the body (0.01 = 1%)
  headRotate: number;
  headX: number;
  headY: number;
  earLeft: number; // relative to head
  earRight: number;
  tail: number;
  bandana: number;
  eyeLeft: number; // closure 0..1 (viewer's left)
  eyeRight: number;
  mouthOpen: number; // 0..1 (values > 1 = a wider "gasp" jaw drop)
  // Optional acting channels (default 0).
  wide?: number; // 0..1 official "Wide" eye state
  hop?: number; // whole-body lift in canvas px (+ = up)
  stretch?: number; // body squash(-)/stretch(+), volume-preserving
};

const clamp = (v: number, [lo, hi]: [number, number] = [-360, 360]) =>
  Math.max(lo, Math.min(hi, v));

const layerStyle = (rig: MiloRig, pivot: Vec, transform: string): React.CSSProperties => ({
  position: "absolute",
  left: 0,
  top: 0,
  width: rig.canvas.width,
  height: rig.canvas.height,
  transformOrigin: `${pivot[0]}px ${pivot[1]}px`,
  transform,
});

// Blinks swap in the official "Half Blink" and "Blink (Closed)" eye-state
// art (pre-fitted per eye by scripts/extract_milo_layers.py). A blink is so
// fast that the brief crossfade between states reads as motion.
const ramp = (v: number, from: number, to: number) =>
  Math.max(0, Math.min(1, (v - from) / (to - from)));

const EyeStates: React.FC<{
  side: "left" | "right";
  closure: number;
  rig: MiloRig;
  wide: number;
}> = ({ side, closure, wide, rig }) => {
  if (closure <= 0.001 && wide <= 0.001) return null;
  const e = rig.eyelid;
  const half = ramp(closure, 0, e.half_full_at);
  const closed = ramp(closure, e.closed_from, e.closed_full_at);
  const style = (opacity: number): React.CSSProperties => ({
    ...layerStyle(rig, [0, 0], "none"),
    opacity,
  });
  return (
    <>
      {wide > 0.001 && <Img src={staticFile(rig.layers[`eye_${side}_wide`].file)} style={style(Math.min(1, wide))} />}
      {half > 0 && <Img src={staticFile(rig.layers[`eye_${side}_half`].file)} style={style(half)} />}
      {closed > 0 && <Img src={staticFile(rig.layers[`eye_${side}_closed`].file)} style={style(closed)} />}
    </>
  );
};

export const MiloPuppet: React.FC<{ rig: MiloRig; pose: MiloPose }> = ({ rig, pose }) => {
  const P = rig.pivots;
  const L = rig.limits_deg;
  const stretch = pose.stretch ?? 0;
  const sy = pose.breath + stretch; // total vertical stretch from the paws
  const sx = -stretch * 0.5; // keep volume: wider when squashed
  const maxOff = rig.limits_px?.head_offset ?? 1e9;

  // Breathing/stretch scales the body from the paws; everything riding on
  // the chest (head, bandana) is lifted by the same amount at its pivot height.
  const lift = (y: number) => -(P.body[1] - y) * sy;
  const headLift = lift(P.head[1]);
  const headTransform =
    `translate(${clamp(pose.headX, [-maxOff, maxOff])}px, ${clamp(pose.headY, [-maxOff, maxOff]) + headLift}px) ` +
    `rotate(${clamp(pose.headRotate, L.head)}deg)`;

  const img = (name: string) => staticFile(rig.layers[name].file);
  const headGroup = (children: React.ReactNode) => (
    <div style={layerStyle(rig, P.head, headTransform)}>{children}</div>
  );

  return (
    <div
      style={{
        position: "relative",
        width: rig.canvas.width,
        height: rig.canvas.height,
        transform: `translateY(${-(pose.hop ?? 0)}px)`,
      }}
    >
      <Img src={img("tail")} style={layerStyle(rig, P.tail, `rotate(${clamp(pose.tail, L.tail)}deg)`)} />
      <Img src={img("body")} style={layerStyle(rig, P.body, `scale(${1 + sx}, ${1 + sy})`)} />
      {headGroup(
        <>
          <Img src={img("head")} style={layerStyle(rig, P.head, "none")} />
          <Img
            src={img("mouth")}
            style={layerStyle(
              rig,
              P.mouth,
              `translateY(${pose.mouthOpen * 3}px) scaleY(${1 + pose.mouthOpen * 0.05})`,
            )}
          />
          <EyeStates side="left" closure={pose.eyeLeft} wide={pose.wide ?? 0} rig={rig} />
          <EyeStates side="right" closure={pose.eyeRight} wide={pose.wide ?? 0} rig={rig} />
        </>,
      )}
      <Img
        src={img("bandana")}
        style={layerStyle(
          rig,
          P.bandana,
          `translateY(${lift(P.bandana[1])}px) scaleX(${1 + sx}) rotate(${clamp(pose.bandana, L.bandana)}deg)`,
        )}
      />
      {headGroup(
        <>
          <Img src={img("ear_left")} style={layerStyle(rig, P.ear_left, `rotate(${clamp(pose.earLeft, L.ear_left)}deg)`)} />
          <Img src={img("ear_right")} style={layerStyle(rig, P.ear_right, `rotate(${clamp(pose.earRight, L.ear_right)}deg)`)} />
        </>,
      )}
    </div>
  );
};
