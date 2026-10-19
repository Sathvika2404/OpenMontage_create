// Milo puppet test scene: Milo on a warm cream backdrop, driven entirely by
// the explicit action timeline passed in as props. `timeline.staging` sets
// framing (defaults reproduce the first 15 s puppet test).

import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { MiloPuppet, MiloRig } from "./MiloPuppet";
import { ActionTimeline, compileTimeline } from "./timeline";

export type MiloPuppetTestProps = {
  rig: MiloRig;
  timeline: ActionTimeline & { staging?: { puppet_scale?: number; floor_y?: number } };
};

export const MiloPuppetTest: React.FC<MiloPuppetTestProps> = ({ rig, timeline }) => {
  const frame = useCurrentFrame();
  const ev = useMemo(() => compileTimeline(timeline), [timeline]);
  const v = (ch: string) => ev(ch, frame);
  const puppetScale = timeline.staging?.puppet_scale ?? 1;
  const FLOOR_Y = timeline.staging?.floor_y ?? 985; // paws on the floor, frame px

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
    hop: v("body.hop"),
    stretch: v("body.stretch"),
  };

  // Puppet is scaled about its paw pivot, which sits on the floor line.
  const left = 960 - rig.pivots.body[0];
  const top = FLOOR_Y - rig.pivots.body[1];
  const hopPx = (pose.hop ?? 0) * puppetScale;
  const shadowK = Math.max(0.6, 1 - hopPx / 120); // shadow shrinks in the air
  // Camera pushes in toward Milo's face (head pivot sits under the chin).
  const focusX = 960;
  const focusY = FLOOR_Y - (rig.pivots.body[1] - rig.pivots.head[1] + 120) * puppetScale + v("camera.focus_y");
  const scale = timeline.channels["camera.scale"] ? v("camera.scale") : 1;

  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse 75% 70% at 50% 42%, #FBF3E6 0%, #F5E8D4 62%, #EEDCC3 100%)",
      }}
    >
      <AbsoluteFill
        style={{
          transformOrigin: `${focusX}px ${focusY}px`,
          transform: `scale(${scale})`,
        }}
      >
        {/* Soft contact shadow so Milo sits on the floor rather than floating. */}
        <div
          style={{
            position: "absolute",
            left: 960 - 250 * puppetScale * shadowK,
            top: FLOOR_Y - 34 * puppetScale,
            width: 500 * puppetScale * shadowK,
            height: 64 * puppetScale,
            opacity: shadowK,
            borderRadius: "50%",
            background:
              "radial-gradient(ellipse at center, rgba(120,84,48,0.30) 0%, rgba(120,84,48,0.12) 45%, rgba(120,84,48,0) 72%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            left,
            top,
            transformOrigin: `${rig.pivots.body[0]}px ${rig.pivots.body[1]}px`,
            transform: `scale(${puppetScale})`,
          }}
        >
          <MiloPuppet rig={rig} pose={pose} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
