import React from "react";
import { Composition } from "remotion";
import { MiloPuppetTest, MiloPuppetTestProps } from "./MiloPuppetTest";
import { WorkshopScene, WorkshopSceneProps } from "./WorkshopScene";

// Props (rig + explicit action timeline) are supplied at render time with
// --props; see scripts/render_puppet_test.py.
const metadata = ({ props }: { props: MiloPuppetTestProps | WorkshopSceneProps }) => ({
  fps: props.timeline?.fps ?? 30,
  durationInFrames: Math.round((props.timeline?.duration_seconds ?? 15) * (props.timeline?.fps ?? 30)),
});

export const Root: React.FC = () => (
  <>
  <Composition
    id="MiloPuppetTest"
    component={MiloPuppetTest}
    width={1920}
    height={1080}
    fps={30}
    durationInFrames={450}
    defaultProps={{} as MiloPuppetTestProps}
    calculateMetadata={metadata}
  />
  {/* Character acting test: same puppet + scene, acting timeline via --props. */}
  <Composition
    id="MiloActingTest"
    component={MiloPuppetTest}
    width={1920}
    height={1080}
    fps={30}
    durationInFrames={450}
    defaultProps={{} as MiloPuppetTestProps}
    calculateMetadata={metadata}
  />
  {/* Scene 01, shots 1-2: Milo + slipper in Grandpa Theo's workshop. */}
  <Composition
    id="Sc01WorkshopSlipper"
    component={WorkshopScene}
    width={1920}
    height={1080}
    fps={30}
    durationInFrames={300}
    defaultProps={{} as WorkshopSceneProps}
    calculateMetadata={metadata}
  />
  </>
);
