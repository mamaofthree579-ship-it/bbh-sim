import streamlit as st
import streamlit.components.v1 as components

st.title("🌌 Multiverse Fractal Simulator")
st.markdown("Visualizing nested quantum-conscious structures across spacetime layers")

html_code = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Fractal Multiverse</title>
    <style>
      body { margin: 0; overflow: hidden; background-color: black; }
      canvas { display: block; width: 100vw; height: 100vh; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r152/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/examples/js/controls/OrbitControls.js"></script>
  </head>
  <body>
    <script>
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 2000);
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      // Lighting
      const ambientLight = new THREE.AmbientLight(0x6666ff, 1.2);
      scene.add(ambientLight);
      const pointLight = new THREE.PointLight(0xffffff, 2, 300);
      pointLight.position.set(0, 0, 0);
      scene.add(pointLight);

      // Orbit Controls
      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.1;

      // Generate fractal nodes
      function generateFractalNodes(level, size, parentPos, spread=1.8) {
          const nodes = [];
          if (level <= 0) return nodes;

          const branches = 3 + Math.floor(Math.random() * 3);
          for (let i = 0; i < branches; i++) {
              const theta = Math.random() * Math.PI * 2;
              const phi = Math.random() * Math.PI;
              const distance = size * (0.6 + Math.random() * 0.4);
              const offset = new THREE.Vector3(
                  Math.sin(phi) * Math.cos(theta) * distance * spread,
                  Math.sin(phi) * Math.sin(theta) * distance * spread,
                  Math.cos(phi) * distance
              );
              const newPos = parentPos.clone().add(offset);
              nodes.push(newPos);
              nodes.push(...generateFractalNodes(level - 1, size * 0.6, newPos, spread * 0.9));
          }
          return nodes;
      }

      // Draw fractal particles
      const material = new THREE.PointsMaterial({ color: 0x88ccff, size: 0.8 });
      const geometry = new THREE.BufferGeometry();

      const positions = [];
      const rootPos = new THREE.Vector3(0, 0, 0);
      const nodes = generateFractalNodes(5, 15, rootPos);

      nodes.forEach(p => {
        positions.push(p.x, p.y, p.z);
      });

      geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      const points = new THREE.Points(geometry, material);
      scene.add(points);

      // Camera position
      camera.position.z = 60;

      // Animation loop
      function animate() {
          requestAnimationFrame(animate);
          points.rotation.y += 0.002;
          controls.update();
          renderer.render(scene, camera);
      }
      animate();

      window.addEventListener('resize', () => {
          camera.aspect = window.innerWidth / window.innerHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(window.innerWidth, window.innerHeight);
      });
    </script>
  </body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
