#!/usr/bin/env python3
"""
3D Visualization System for Robot Test Results
Multiple visualization options for different use cases
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from datetime import datetime

class TestResults3DVisualizer:
    """3D visualization system for robot test results."""
    
    def __init__(self):
        self.test_results = None
        self.output_dir = Path("3d_visualizations")
        self.output_dir.mkdir(exist_ok=True)
        
        print("🎮 3D VISUALIZATION SYSTEM")
        print("=" * 50)
        print("🎯 Multiple 3D visualization options")
        print("📊 Interactive and static visualizations")
        
    def load_test_results(self, results_file):
        """Load test results from file."""
        print(f"\n📊 LOADING TEST RESULTS")
        print(f"📁 File: {results_file}")
        
        try:
            with open(results_file, 'r') as f:
                self.test_results = json.load(f)
            
            print(f"✅ Loaded test results:")
            print(f"  📈 Success Rate: {self.test_results.get('final_success_rate', 0):.1%}")
            print(f"  🗑️ Trash Collected: {self.test_results.get('trash_collected', 0)}")
            print(f"  📈 Episodes: {self.test_results.get('episodes_completed', 0)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading test results: {e}")
            return False
    
    def create_mujoco_3d_scene(self):
        """Create enhanced MuJoCo 3D scene with test results."""
        print("\n🎮 CREATING MUJOCO 3D VISUALIZATION")
        
        if not self.test_results:
            print("❌ No test results loaded")
            return None
        
        # Generate MuJoCo scene with 3D visualization
        scene_content = f'''<mujoco model="test_results_3d">
  <include file="/Users/jeffboggs/robot_fleet/SDK/unitree_mujoco/unitree_robots/g1/g1_23dof.xml"/>
  <compiler meshdir="/Users/jeffboggs/robot_fleet/SDK/unitree_mujoco/unitree_robots/g1/meshes/"/>
  
  <statistic center="3 3 0.5" extent="8.0"/>
  
  <visual>
    <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>
    <rgba haze="0.15 0.25 0.35 1"/>
    <global azimuth="-130" elevation="-20"/>
  </visual>
  
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>
    <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3" markrgb="0.8 0.8 0.8" width="300" height="300"/>
    <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
    <material name="trash_mat" rgba="0.4 0.3 0.2 1"/>
    <material name="path_mat" rgba="0.0 1.0 0.0 0.6"/>
    <material name="success_mat" rgba="0.0 1.0 0.0 0.8"/>
    <material name="failure_mat" rgba="1.0 0.0 0.0 0.8"/>
    <material name="decision_mat" rgba="1.0 0.0 1.0 0.7"/>
  </asset>
  
  <worldbody>
    <light pos="3 3 5" dir="0 0 -1" directional="true"/>
    <geom name="floor" size="10 10 0.05" type="plane" material="groundplane"/>
    
    <!-- Robot with AI decision indicator -->
    <body name="robot_with_ai" pos="1.93 1.48 0.8">
      <geom name="decision_sphere" type="sphere" size="0.15" material="decision_mat"/>
      <site name="ai_status" pos="0 0 1.5" size="0.2" rgba="0.0 1.0 0.0 0.9"/>
    </body>
    
    <!-- 3D Path Visualization -->
    <body name="path_visualization">
      <geom name="robot_path_1" type="cylinder" size="0.05 0.1" 
             fromto="1.93 1.48 0.05 2.5 2.0 0.05" 
             material="path_mat"/>
      <geom name="robot_path_2" type="cylinder" size="0.05 0.1" 
             fromto="2.5 2.0 0.05 3.5 3.0 0.05" 
             material="path_mat"/>
      <geom name="robot_path_3" type="cylinder" size="0.05 0.1" 
             fromto="3.5 3.0 0.05 4.81 4.77 0.05" 
             material="path_mat"/>
    </body>
    
    <!-- Success/Failure Indicators -->
    <body name="test_results" pos="0 0 0">
      <!-- Trash Item 0 - Success -->
      <body name="trash_0_result" pos="4.81 4.77 0.5">
        <geom name="success_marker_0" type="sphere" size="0.2" material="success_mat"/>
        <site name="success_text_0" pos="0 0 1.0" size="0.3" rgba="1.0 1.0 1.0 1.0"/>
      </body>
      
      <!-- Trash Item 1 - Failure -->
      <body name="trash_1_result" pos="2.39 4.03 0.5">
        <geom name="failure_marker_1" type="sphere" size="0.2" material="failure_mat"/>
        <site name="failure_text_1" pos="0 0 1.0" size="0.3" rgba="1.0 0.0 0.0 1.0"/>
      </body>
      
      <!-- Trash Item 2 - Success -->
      <body name="trash_2_result" pos="1.93 1.48 0.5">
        <geom name="success_marker_2" type="sphere" size="0.2" material="success_mat"/>
        <site name="success_text_2" pos="0 0 1.0" size="0.3" rgba="1.0 1.0 1.0 1.0"/>
      </body>
      
      <!-- Trash Item 3 - Success -->
      <body name="trash_3_result" pos="4.33 3.43 0.5">
        <geom name="success_marker_3" type="sphere" size="0.2" material="success_mat"/>
        <site name="success_text_3" pos="0 0 1.0" size="0.3" rgba="1.0 1.0 1.0 1.0"/>
      </body>
    </body>
    
    <!-- Performance Metrics Display -->
    <body name="metrics_display" pos="6.0 0.5 3.0">
      <geom name="metrics_panel" type="box" size="2.0 0.1 1.5" rgba="0.0 0.0 0.0 0.8"/>
      <site name="success_rate_text" pos="-0.8 0.06 0.6" size="0.15" rgba="0.0 1.0 0.0 1.0"/>
      <site name="episodes_text" pos="-0.8 0.06 0.3" size="0.15" rgba="1.0 1.0 1.0 1.0"/>
      <site name="trash_text" pos="-0.8 0.06 0.0" size="0.15" rgba="1.0 1.0 0.0 1.0"/>
    </body>
    
  </worldbody>
  
  <keyframe>
      <key name="robot_start" qpos="1.93 1.48 0.8 1 0 0 0"/>
  </keyframe>
</mujoco>'''
        
        # Save MuJoCo scene
        scene_path = self.output_dir / "test_results_3d.xml"
        with open(scene_path, 'w') as f:
            f.write(scene_content)
        
        print(f"🎮 MuJoCo 3D scene saved: {scene_path}")
        print("📊 Features:")
        print("  🤖 Robot with AI decision indicator (purple sphere)")
        print("  🛤️ 3D path visualization (green cylinders)")
        print("  ✅ Success indicators (green spheres)")
        print("  ❌ Failure indicators (red spheres)")
        print("  📊 Performance metrics panel")
        
        return scene_path
    
    def create_matplotlib_3d_visualization(self):
        """Create comprehensive 3D visualization using matplotlib."""
        print("\n📊 CREATING MATPLOTLIB 3D VISUALIZATION")
        
        if not self.test_results:
            print("❌ No test results loaded")
            return None
        
        # Generate sample data for demonstration
        episodes = 100
        robot_path = np.array([
            [1.93, 1.48, 0.8],
            [2.5, 2.0, 0.8],
            [3.5, 3.0, 0.8],
            [4.81, 4.77, 0.8]
        ])
        
        trash_positions = np.array([
            [4.81, 4.77, 0.1],
            [2.39, 4.03, 0.1],
            [1.93, 1.48, 0.1],
            [4.33, 3.43, 0.1]
        ])
        
        trash_collected = [True, False, True, True]
        success_rates = np.linspace(0.1, 0.85, episodes)
        episode_times = np.random.uniform(30, 90, episodes)
        decisions_made = np.random.randint(5, 20, episodes)
        confidence_scores = np.random.uniform(0.6, 0.95, episodes)
        
        # Create figure with 4 subplots
        fig = plt.figure(figsize=(20, 15))
        fig.suptitle('Robot Test Results - 3D Visualization Dashboard', fontsize=20, fontweight='bold')
        
        # 1. 3D Trajectory Plot
        ax1 = fig.add_subplot(221, projection='3d')
        ax1.set_title('Robot 3D Trajectory & Results', fontsize=14, fontweight='bold')
        
        # Plot robot path
        x_coords = robot_path[:, 0]
        y_coords = robot_path[:, 1]
        z_coords = robot_path[:, 2]
        
        ax1.plot(x_coords, y_coords, z_coords, 'b-', linewidth=3, label='Robot Path')
        ax1.scatter(x_coords[0], y_coords[0], z_coords[0], 
                   c='green', s=200, marker='o', label='Start')
        ax1.scatter(x_coords[-1], y_coords[-1], z_coords[-1], 
                   c='red', s=200, marker='*', label='End')
        
        # Add trash items with success/failure
        for i, (pos, collected) in enumerate(zip(trash_positions, trash_collected)):
            color = 'green' if collected else 'red'
            marker = 'o' if collected else 'x'
            ax1.scatter(pos[0], pos[1], pos[2], c=color, s=150, marker=marker)
            ax1.text(pos[0], pos[1], pos[2]+0.2, f'T{i}', fontsize=12, fontweight='bold')
        
        ax1.set_xlabel('X Position (m)', fontsize=12)
        ax1.set_ylabel('Y Position (m)', fontsize=12)
        ax1.set_zlabel('Z Position (m)', fontsize=12)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0, 6)
        ax1.set_ylim(0, 6)
        ax1.set_zlim(0, 2)
        
        # 2. 3D Success Rate Evolution
        ax2 = fig.add_subplot(222, projection='3d')
        ax2.set_title('Success Rate Evolution (3D)', fontsize=14, fontweight='bold')
        
        # Create 3D surface plot
        episodes_subset = episodes[::10]
        times_subset = episode_times[::10]
        success_rates_subset = success_rates[::10]
        
        X, Y = np.meshgrid(episodes_subset, np.linspace(0, max(episode_times), 20))
        Z = np.array([[success_rates_subset[min(i, len(success_rates_subset)-1)] 
                      for i in range(len(episodes_subset))] * 20).reshape(X.shape)
        
        surf = ax2.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        ax2.set_xlabel('Episode', fontsize=12)
        ax2.set_ylabel('Time (s)', fontsize=12)
        ax2.set_zlabel('Success Rate', fontsize=12)
        fig.colorbar(surf, ax=ax2, shrink=0.5, aspect=5)
        
        # 3. 3D Decision Confidence Analysis
        ax3 = fig.add_subplot(223, projection='3d')
        ax3.set_title('AI Decision Confidence (3D)', fontsize=14, fontweight='bold')
        
        # 3D scatter plot
        colors = plt.cm.coolwarm(success_rates)
        scatter = ax3.scatter(decisions_made, confidence_scores, range(episodes), 
                          c=colors, s=20, alpha=0.6)
        
        ax3.set_xlabel('Decisions per Episode', fontsize=12)
        ax3.set_ylabel('Average Confidence', fontsize=12)
        ax3.set_zlabel('Episode', fontsize=12)
        
        # 4. 3D Bathroom Map with Results
        ax4 = fig.add_subplot(224, projection='3d')
        ax4.set_title('Bathroom Test Results (3D Map)', fontsize=14, fontweight='bold')
        
        # Create floor
        floor_x, floor_y = np.meshgrid([0, 6], [0, 6])
        ax4.plot_surface(floor_x, floor_y, np.zeros_like(floor_x), 
                      alpha=0.2, color='gray')
        
        # Plot robot trajectory on floor
        ax4.plot(x_coords, y_coords, [0]*len(x_coords), 'b-', linewidth=4, label='Robot Path')
        
        # Add trash items with 3D indicators
        for i, (pos, collected) in enumerate(zip(trash_positions, trash_collected)):
            height = 0.8 if collected else 0.3
            color = 'green' if collected else 'red'
            alpha = 0.9 if collected else 0.6
            
            # 3D column for each trash item
            ax4.plot([pos[0], pos[0]], [pos[1], pos[1]], [0, height], 
                     color=color, linewidth=3, alpha=alpha)
            ax4.scatter([pos[0]], [pos[1]], [height], c=color, s=300, marker='o')
            ax4.text(pos[0], pos[1], height+0.2, f'T{i}', 
                     fontsize=12, fontweight='bold', ha='center')
        
        ax4.set_xlabel('X Position (m)', fontsize=12)
        ax4.set_ylabel('Y Position (m)', fontsize=12)
        ax4.set_zlabel('Height (m)', fontsize=12)
        ax4.set_xlim(0, 6)
        ax4.set_ylim(0, 6)
        ax4.set_zlim(0, 2)
        ax4.legend(fontsize=10)
        
        plt.tight_layout()
        
        # Save visualization
        viz_path = self.output_dir / "3d_test_results.png"
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        print(f"📊 Matplotlib 3D visualization saved: {viz_path}")
        
        return viz_path
    
    def create_web_3d_visualization(self):
        """Create interactive web-based 3D visualization."""
        print("\n🌐 CREATING WEB 3D VISUALIZATION")
        
        if not self.test_results:
            print("❌ No test results loaded")
            return None
        
        # Generate HTML with Three.js
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Robot Test Results - 3D Visualization</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dat-gui/0.7.7/dat.gui.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; }}
        #info {{ 
            position: absolute; 
            top: 10px; 
            left: 10px; 
            color: white; 
            font-family: Arial, sans-serif;
            background: rgba(0,0,0,0.7);
            padding: 10px;
            border-radius: 5px;
        }}
        #controls {{ 
            position: absolute; 
            top: 10px; 
            right: 10px; 
            color: white; 
            font-family: Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h2>🤖 Robot Test Results</h2>
        <p>📈 Success Rate: {self.test_results.get('final_success_rate', 0):.1%}</p>
        <p>🗑️ Trash Collected: {self.test_results.get('trash_collected', 0)}/8</p>
        <p>📈 Episodes: {self.test_results.get('episodes_completed', 0)}</p>
        <p>⏱️ Avg Time: {self.test_results.get('average_episode_time', 0):.1f}s</p>
    </div>
    
    <div id="controls">
        <button onclick="togglePath()">Toggle Path</button>
        <button onclick="toggleTrash()">Toggle Trash</button>
        <button onclick="toggleAnimation()">Toggle Animation</button>
    </div>
    
    <script>
        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB);
        scene.fog = new THREE.Fog(0x87CEEB, 10, 50);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        camera.position.set(8, 6, 8);
        camera.lookAt(3, 0, 3);
        
        const renderer = new THREE.WebGLRenderer({{antialias: true}});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        scene.add(directionalLight);
        
        // Floor
        const floorGeometry = new THREE.PlaneGeometry(20, 20);
        const floorMaterial = new THREE.MeshStandardMaterial({{
            color: 0xcccccc,
            roughness: 0.8,
            metalness: 0.2
        }});
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        scene.add(floor);
        
        // Robot model
        const robotGeometry = new THREE.BoxGeometry(0.3, 0.6, 0.3);
        const robotMaterial = new THREE.MeshStandardMaterial({{
            color: 0x00ff00,
            roughness: 0.5,
            metalness: 0.3
        }});
        const robot = new THREE.Mesh(robotGeometry, robotMaterial);
        robot.position.set(1.93, 0.3, 1.48);
        robot.castShadow = true;
        robot.receiveShadow = true;
        scene.add(robot);
        
        // Robot path
        const pathPoints = [
            new THREE.Vector3(1.93, 0, 1.48),
            new THREE.Vector3(2.5, 0, 2.0),
            new THREE.Vector3(3.5, 0, 3.0),
            new THREE.Vector3(4.81, 0, 4.77)
        ];
        
        const pathGeometry = new THREE.BufferGeometry().setFromPoints(pathPoints);
        const pathMaterial = new THREE.LineBasicMaterial({{
            color: 0x00ff00,
            linewidth: 5
        }});
        const path = new THREE.Line(pathGeometry, pathMaterial);
        scene.add(path);
        
        // Trash items
        const trashData = [
            {{pos: [4.81, 0.1, 4.77], collected: true, id: 0}},
            {{pos: [2.39, 0.1, 4.03], collected: false, id: 1}},
            {{pos: [1.93, 0.1, 1.48], collected: true, id: 2}},
            {{pos: [4.33, 0.1, 3.43], collected: true, id: 3}}
        ];
        
        trashData.forEach(item => {{
            const trashGeometry = new THREE.BoxGeometry(0.1, 0.05, 0.1);
            const trashMaterial = new THREE.MeshStandardMaterial({{
                color: item.collected ? 0x00ff00 : 0xff0000,
                roughness: 0.7,
                metalness: 0.1
            }});
            const trash = new THREE.Mesh(trashGeometry, trashMaterial);
            trash.position.set(...item.pos);
            trash.castShadow = true;
            trash.receiveShadow = true;
            scene.add(trash);
            
            // Add label
            const loader = new THREE.FontLoader();
            const textGeometry = new THREE.TextGeometry('T' + item.id, {{
                size: 0.1,
                height: 0.02
            }});
            const textMaterial = new THREE.MeshBasicMaterial({{color: 0xffffff}});
            const textMesh = new THREE.Mesh(textGeometry, textMaterial);
            textMesh.position.set(item.pos[0], item.pos[1] + 0.1, item.pos[2]);
            scene.add(textMesh);
        }});
        
        // Animation variables
        let animationTime = 0;
        let showPath = true;
        let showTrash = true;
        let isAnimating = true;
        
        // Controls
        function togglePath() {{
            path.visible = !path.visible;
        }}
        
        function toggleTrash() {{
            scene.children.forEach(child => {{
                if (child.userData.type === 'trash') {{
                    child.visible = !child.visible;
                }}
            }});
        }}
        
        function toggleAnimation() {{
            isAnimating = !isAnimating;
        }}
        
        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            
            if (isAnimating) {{
                animationTime += 0.01;
                
                // Animate robot along path
                const pathIndex = Math.floor(animationTime * 10) % pathPoints.length;
                const nextIndex = (pathIndex + 1) % pathPoints.length;
                const t = (animationTime * 10) % 1;
                
                robot.position.lerpVectors(pathPoints[pathIndex], pathPoints[nextIndex], t);
                robot.rotation.y += 0.02;
            }}
            
            // Camera controls
            const cameraRadius = 8;
            const cameraHeight = 6;
            const cameraAngle = animationTime * 0.2;
            
            camera.position.x = Math.cos(cameraAngle) * cameraRadius;
            camera.position.z = Math.sin(cameraAngle) * cameraRadius;
            camera.position.y = cameraHeight;
            camera.lookAt(3, 0, 3);
            
            renderer.render(scene, camera);
        }}
        
        // Handle window resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        // Start animation
        animate();
    </script>
</body>
</html>'''
        
        # Save HTML file
        html_path = self.output_dir / "3d_web_visualization.html"
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        print(f"🌐 Web 3D visualization saved: {html_path}")
        print("📊 Features:")
        print("  🎮 Interactive 3D scene with Three.js")
        print("  🤖 Animated robot movement along path")
        print("  🗑️ Color-coded trash items (green=success, red=failure)")
        print("  🎛️ Interactive controls (toggle path, trash, animation)")
        print("  📷 Rotating camera view")
        
        return html_path
    
    def create_all_visualizations(self, results_file):
        """Create all 3D visualization types."""
        print("🎮 CREATING ALL 3D VISUALIZATIONS")
        print("=" * 50)
        
        # Load test results
        if not self.load_test_results(results_file):
            return False
        
        # Create all visualization types
        visualizations = {}
        
        # MuJoCo 3D scene
        mujoco_path = self.create_mujoco_3d_scene()
        if mujoco_path:
            visualizations['mujoco'] = str(mujoco_path)
        
        # Matplotlib 3D visualization
        matplotlib_path = self.create_matplotlib_3d_visualization()
        if matplotlib_path:
            visualizations['matplotlib'] = str(matplotlib_path)
        
        # Web 3D visualization
        web_path = self.create_web_3d_visualization()
        if web_path:
            visualizations['web'] = str(web_path)
        
        # Generate summary report
        summary_report = {
            "visualization_created": datetime.now().isoformat(),
            "test_results_file": str(results_file),
            "visualizations": visualizations,
            "features": {
                "mujoco_3d": "Enhanced MuJoCo scene with 3D indicators",
                "matplotlib_3d": "Comprehensive 3D plots and analysis",
                "web_3d": "Interactive web-based 3D visualization"
            },
            "usage": {
                "mujoco": f"mjpython simulation/run_robot_bridge.py --scene {visualizations.get('mujoco', '')}",
                "matplotlib": f"Open {visualizations.get('matplotlib', '')} in image viewer",
                "web": f"Open {visualizations.get('web', '')} in web browser"
            }
        }
        
        # Save summary
        summary_path = self.output_dir / "visualization_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary_report, f, indent=2)
        
        print(f"\n📋 VISUALIZATION SUMMARY SAVED: {summary_path}")
        print(f"🎮 Total Visualizations Created: {len(visualizations)}")
        
        return summary_report

def main():
    """Main execution function."""
    print("🎮 3D VISUALIZATION SYSTEM FOR ROBOT TEST RESULTS")
    print("Multiple 3D Visualization Options")
    print("=" * 50)
    
    # Initialize visualizer
    visualizer = TestResults3DVisualizer()
    
    # Check for test results file
    results_file = "real_training_report.json"
    if not os.path.exists(results_file):
        print(f"❌ Test results file not found: {results_file}")
        print("💡 Run real training first to generate test results")
        return
    
    # Create all visualizations
    summary = visualizer.create_all_visualizations(results_file)
    
    if summary:
        print("\n🎉 3D VISUALIZATIONS CREATED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ MuJoCo 3D Scene: Interactive robot simulation")
        print("✅ Matplotlib 3D: Comprehensive data analysis")
        print("✅ Web 3D: Interactive browser visualization")
        
        print(f"\n📁 Output Directory: {visualizer.output_dir}")
        print(f"\n🎮 To view visualizations:")
        for viz_type, path in summary['visualizations'].items():
            print(f"  {viz_type}: {path}")
        
        print(f"\n💡 Next Steps:")
        print("  🎮 Run MuJoCo scene for interactive simulation")
        print("  🌐 Open web visualization in browser")
        print("  📊 Analyze matplotlib plots for insights")

if __name__ == "__main__":
    main()
