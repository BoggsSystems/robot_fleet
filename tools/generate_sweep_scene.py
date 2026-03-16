import os

SCENE_PATH = "/Users/jeffboggs/robot_fleet/SDK/unitree_mujoco/unitree_robots/g1/inventory_sweep_scene.xml"

def generate_scene():
    xml = [
        '<mujoco model="inventory_sweep">',
        '  <include file="g1_23dof.xml"/>',
        '',
        '  <statistic center="5 0 0.5" extent="10.0"/>',
        '',
        '  <visual>',
        '    <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>',
        '    <rgba haze="0.15 0.25 0.35 1"/>',
        '    <global azimuth="-130" elevation="-20"/>',
        '  </visual>',
        '',
        '  <asset>',
        '    <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>',
        '    <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"',
        '      markrgb="0.8 0.8 0.8" width="300" height="300"/>',
        '    <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>',
        '    <material name="shelf_mat" rgba="0.6 0.6 0.6 1"/>',
        '    <material name="box_mat" rgba="0.8 0.4 0.2 1"/>',
        '    <material name="target_mat" rgba="0.2 0.8 0.2 1"/>',
        '  </asset>',
        '',
        '  <worldbody>',
        '    <light pos="0 0 10" dir="0 0 -1" directional="true"/>',
        '    <geom name="floor" size="10 2 0.05" type="plane" material="groundplane"/>',
        ''
    ]

    # Generate Shelves and Boxes along the X axis
    # Robot starts at X=0, walks toward X=10
    # Aligned on Y=0.8
    shelf_x_start = 1.0
    shelf_x_end = 9.0
    y_offset = 0.8  # Distance from center of aisle to shelf
    
    # 1. Continuous Shelf geom
    xml.append(f'    <geom name="aisle_shelf" type="box" size="4.5 0.3 0.6" pos="5.0 {y_offset} 0.6" material="shelf_mat"/>')
    
    # 2. Procedural Boxes
    # Place boxes on the shelf (Z=1.2 is top of shelf)
    import random
    random.seed(42) # Deterministic for now
    
    for i in range(25):
        # Random X along the shelf
        x = shelf_x_start + (i * 0.32) # Spread them out
        if x > shelf_x_end: break
        
        # Randomize Z slightly (some on shelf, some maybe stacked?)
        z = 1.2 + 0.15 # Box height is 0.3 (size 0.15)
        
        # Higher confidence "Target Boxes" in green
        mat = "box_mat"
        if random.random() > 0.8:
            mat = "target_mat"
            
        xml.append(f'    <body name="box_{i}" pos="{x:.2f} {y_offset:.2f} {z:.2f}">')
        xml.append('        <freejoint/>')
        xml.append(f'        <geom name="box_geom_{i}" type="box" size="0.15 0.15 0.15" material="{mat}" condim="3" friction="0.5 0.005 0.0001"/>')
        xml.append('        <inertial pos="0 0 0" mass="1.0" diaginertia="0.01 0.01 0.01"/>')
        xml.append('    </body>')

    xml.append('  </worldbody>')
    xml.append('</mujoco>')

    with open(SCENE_PATH, "w") as f:
        f.write("\n".join(xml))
    print(f"Generated scene at {SCENE_PATH}")

if __name__ == "__main__":
    generate_scene()
