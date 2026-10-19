// Scene 01 (workshop): Milo's approved sitting puppet placed in the painted
// workshop plate, with a camera that frames the world in background-image
// pixels. Everything (camera, acting, light) is driven by one explicit
// timeline; cuts are just instant changes in the camera channels.

import React, { useMemo } from "react";
import { AbsoluteFill, Img, random, staticFile, useCurrentFrame } from "remotion";
import { MiloPuppet, MiloRig } from "./MiloPuppet";
import { ActionTimeline, compileTimeline } from "./timeline";

type Vec = [number, number];

export type WorkshopLayout = {
  world: { width: number; height: number; background: string };
  milo: { x: number; floor_y: number; height: number; filter: string };
  slipper: {
    src: string;
    heel_x: number; // world x of the slipper's left (heel) end
    floor_y: number; // world y of the sole
    length: number; // world px, heel to toe
    aspect: number; // trimmed image height / width (written by the render script)
    filter: string;
  };
  light: {
    shafts: { points: Vec[]; opacity: number }[];
    dust: { count: number; region: [number, number, number, number]; seed: string };
  };
  shadow: { color: string; cast_skew_deg: number; cast_scale_y: number; cast_opacity: number };
};

export type WorkshopSceneProps = {
  rig: MiloRig;
  timeline: ActionTimeline & { layout: WorkshopLayout };
};

// Keep the painted plate covering the whole frame whatever the timeline asks.
const clampCamera = (s: number, cx: number, cy: number, w: number, h: number) => {
  const scale = Math.max(s, 1920 / w, 1080 / h);
  const hw = 960 / scale;
  const hh = 540 / scale;
  return {
    scale,
    cx: Math.min(Math.max(cx, hw), w - hw),
    cy: Math.min(Math.max(cy, hh), h - hh),
  };
};

const DustMotes: React.FC<{ layout: WorkshopLayout; frame: number; fps: number }> = ({
  layout,
  frame,
  fps,
}) => {
  const { count, region, seed } = layout.light.dust;
  const [x0, y0, x1, y1] = region;
  const t = frame / fps;
  return (
    <>
      {Array.from({ length: count }, (_, i) => {
        const r = (k: string) => random(`${seed}-${i}-${k}`);
        const w = x1 - x0;
        const h = y1 - y0;
        // Slow upward/rightward drift with gentle sway, wrapped in the region.
        const x = x0 + ((r("x") * w + t * (2 + r("vx") * 4)) % w) + Math.sin(t * (0.4 + r("f") * 0.6) + r("p") * 6) * 6;
        const y = y0 + (((r("y") * h - t * (1.5 + r("vy") * 3)) % h) + h) % h;
        const size = 0.9 + r("s") * 1.6;
        const twinkle = 0.45 + 0.55 * Math.abs(Math.sin(t * (0.6 + r("tw")) + r("tp") * 6));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x - size,
              top: y - size,
              width: size * 2,
              height: size * 2,
              borderRadius: "50%",
              background: "radial-gradient(circle, rgba(255,240,200,0.95) 0%, rgba(255,220,150,0) 70%)",
              opacity: 0.55 * twinkle,
            }}
          />
        );
      })}
    </>
  );
};

export const WorkshopScene: React.FC<WorkshopSceneProps> = ({ rig, timeline }) => {
  const frame = useCurrentFrame();
  const ev = useMemo(() => compileTimeline(timeline), [timeline]);
  const v = (ch: string) => ev(ch, frame);
  const L = timeline.layout;
  const W = L.world.width;
  const H = L.world.height;

  const cam = clampCamera(v("camera.scale"), v("camera.x"), v("camera.y"), W, H);
  const bgBlur = v("bg.blur");

  const pose = {
    breath: v("body.breath"),
    headRotate: v("head.rotate"),
    headX: v("head.x"),
    headY: v("head.y"),
    earLeft: v("ear_left.rotate"),
    earRight: v("ear_right.rotate"),
    tail: v("tail.rotate"),
    bandana: v("bandana.rotate"),
    eyeLeft: v("eye_left.closure"),
    eyeRight: v("eye_right.closure"),
    mouthOpen: v("mouth.open"),
    wide: v("eyes.wide"),
  };

  // Milo: rig canvas scaled so its paw pivot sits on the floor point.
  const k = L.milo.height / rig.canvas.height;
  const [px, py] = rig.pivots.body;
  const miloLeft = L.milo.x - px * k;
  const miloTop = L.milo.floor_y - py * k;
  const miloW = rig.canvas.width * k;

  // Slipper: trimmed image (heel on the left), sole on the floor line.
  const sl = L.slipper;
  const slH = sl.length * sl.aspect;
  const slTop = sl.floor_y - slH;
  const sh = L.shadow;

  const castShadow = (src: string, left: number, top: number, w: number, h: number, origin: string) => (
    <Img
      src={staticFile(src)}
      style={{
        position: "absolute",
        left,
        top,
        width: w,
        height: h,
        transformOrigin: origin,
        // Flattened onto the floor from the contact line and sheared away
        // from the window (light travels left to right across the floor).
        transform: `skewX(${sh.cast_skew_deg}deg) scaleY(${sh.cast_scale_y})`,
        filter: "brightness(0) blur(4px)",
        opacity: sh.cast_opacity,
      }}
    />
  );

  return (
    <AbsoluteFill style={{ background: "#2a1a0e", overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: W,
          height: H,
          transformOrigin: "0 0",
          transform: `translate(960px, 540px) scale(${cam.scale}) translate(${-cam.cx}px, ${-cam.cy}px)`,
        }}
      >
        <Img
          src={staticFile(L.world.background)}
          style={{ position: "absolute", left: 0, top: 0, width: W, height: H, filter: bgBlur > 0.01 ? `blur(${bgBlur}px)` : undefined }}
        />

        {/* Window light shafts (screen blend), breathing very slowly. */}
        {L.light.shafts.map((s, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              inset: 0,
              clipPath: `polygon(${s.points.map(([x, y]) => `${x}px ${y}px`).join(", ")})`,
              background: "linear-gradient(115deg, rgba(255,214,140,0.9) 0%, rgba(255,190,110,0.35) 55%, rgba(255,180,100,0) 100%)",
              mixBlendMode: "screen",
              filter: "blur(6px)",
              opacity: s.opacity * (0.8 + 0.2 * Math.sin(frame / 30 * 0.7 + i * 1.7)),
            }}
          />
        ))}

        {/* Floor shadows: soft cast shadows away from the window + contact AO. */}
        {castShadow("scene/slipper.png", sl.heel_x, slTop, sl.length, slH, `50% 100%`)}
        {castShadow("layers/_reference_cutout.png", miloLeft, miloTop, miloW, L.milo.height, `${px * k}px 100%`)}
        <div
          style={{
            position: "absolute",
            left: sl.heel_x + sl.length * 0.01,
            top: sl.floor_y - 8,
            width: sl.length * 0.98,
            height: 16,
            borderRadius: "50%",
            background: `radial-gradient(ellipse at center, ${sh.color} 0%, rgba(40,20,8,0.25) 50%, rgba(40,20,8,0) 75%)`,
          }}
        />
        {/* Tight occlusion line where the sole meets the planks. */}
        <div
          style={{
            position: "absolute",
            left: sl.heel_x + sl.length * 0.03,
            top: sl.floor_y - 4,
            width: sl.length * 0.94,
            height: 7,
            borderRadius: "50%",
            background: "radial-gradient(ellipse at center, rgba(20,8,2,0.85) 0%, rgba(20,8,2,0.4) 55%, rgba(20,8,2,0) 80%)",
            filter: "blur(0.6px)",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: L.milo.x - miloW * 0.4,
            top: L.milo.floor_y - 11,
            width: miloW * 0.8,
            height: 18,
            borderRadius: "50%",
            background: `radial-gradient(ellipse at center, ${sh.color} 0%, rgba(40,20,8,0.25) 50%, rgba(40,20,8,0) 75%)`,
          }}
        />

        {/* Slipper (behind Milo: it sits a few px further back on the floor). */}
        <Img
          src={staticFile(sl.src)}
          style={{ position: "absolute", left: sl.heel_x, top: slTop, width: sl.length, height: slH, filter: sl.filter }}
        />

        {/* Milo: approved sitting puppet, graded into the warm window light. */}
        <div
          style={{
            position: "absolute",
            left: miloLeft,
            top: miloTop,
            transformOrigin: "0 0",
            transform: `scale(${k})`,
            filter: L.milo.filter,
          }}
        >
          <MiloPuppet rig={rig} pose={pose} />
        </div>

        <DustMotes layout={L} frame={frame} fps={timeline.fps} />
      </div>

      {/* Gentle vignette to hold the eye on the action. */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 80% 75% at 50% 55%, rgba(0,0,0,0) 60%, rgba(30,12,0,0.35) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
