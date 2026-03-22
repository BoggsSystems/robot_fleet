import random

def generate_trash_xml(num_items=5):
    items_xml = ""
    for i in range(num_items):
        # Random position in the main floor area (avoiding walls/fixtures)
        x = random.uniform(1.0, 5.0)
        y = random.uniform(1.0, 5.0)
        z = 0.1 # Just above floor
        
        items_xml += f"""
    <body name="trash_{i}" pos="{x:.2f} {y:.2f} {z:.2f}">
        <freejoint/>
        <geom name="trash_geom_{i}" type="box" size="0.05 0.05 0.02" material="trash_mat" mass="0.1" friction="0.8 0.005 0.0001"/>
        <inertial pos="0 0 0" mass="0.1" diaginertia="0.001 0.001 0.001"/>
    </body>"""
    return items_xml

if __name__ == "__main__":
    with open("/Users/jeffboggs/robot_fleet/simulation/bathroom_scene.xml", "r") as f:
        content = f.read()
    
    trash_content = generate_trash_xml(8)
    new_content = content.replace("<!-- Trash items will be injected here -->", trash_content)
    
    with open("/Users/jeffboggs/robot_fleet/simulation/bathroom_scene.xml", "w") as f:
        f.write(new_content)
    print("Injected 8 random trash items into bathroom_scene.xml")
