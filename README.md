# halo-conveyor
Blender extension for making Halo conveyor belts and escalators. Conveyor surfaces were added in Halo2, but removed afterwards. So in Halo4 onwards we have to use "device machine" setups.

# Installation
Download the code as zip, install the add-on from prefrences menu.

# How to use
0. Create a scale model of MasterChief or Arbiter for reference.
1. Create a BezierCircle called `BezierCircle`
2. Create a cube called `step` to be your render mesh
3. Create a cube called `step_phys` to be your physics mesh
4. Create a cube called `step_col` to be your collision mesh
5. Create an Armature called "Armature" with a single bone called `root`
6. Position the Armature at the exact same position as the BezierCircle
7. Select any object in object mode and Click `Execute` to generate bones along the path with attached copies of the meshes.
8. Select the armature, go into Pose mode
9. Select one of the newly created bones, go to bone constraints, click "Animate Path".  You only need to do this once on one bone
10. Play the animation to test it.
11. To give the machine a main body, create a mesh and parent it to the root bone.

# Exporting to halo
0. Follow the device machine tutorial on c20 to understand the process
1. Export jms
2. Export jmo (under jma) and save an animation called `device position`
3. Use tool
    - `tool render path\in\data\folder draft`
    - `tool model-animations path\in\data\folder`
    - `tool physics path\in\data\folder`
    - `tool collision path\in\data\folder`
4. Use Guerilla
    - Create new model tag
        - select the render model, collision model, animation, physics model
    - Create new device machine tag
        - select the model you just created above
        - set bounding radius to something large like 10
        - set position transition time to 10 seconds.  Larger is slower.
        - set type to `gear`
5. Add to you level using Sapien

# Tips
- If you want to slow things down or you want more keyframes then you can set a larger number in the timeline.  Then, on the BezierCircle, under `Path Animation` you can adjust the number of frames to match.  Then re-adjust the spacing.  You can also adjust the speed in Guerilla on the device.
- To smooth out the path, on the BezierCircle under `Active Spline` increase `Resolution U`
- Make sure the meshes all have a material. Otherwise you will get `index>=0 && index<array->count` error when exporting the jms.
- Use "update spacing only" to adjust spacing after clicking execute, it is faster.