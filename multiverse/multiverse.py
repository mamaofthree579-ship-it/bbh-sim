import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Fractal Conscious Cosmos", layout="wide")

st.title("🌌 Fractal Conscious Cosmos — 3D Visualizer (Diagnostic Build)")
st.write("This version verifies whether WebGL initializes correctly in your environment.")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<base href="/" />
<title>Fractal Conscious Cosmos 3D Diagnostic</title>
<style>
  body { margin: 0; overflow: hidden; background-color: #000; }
  #debug { position: absolute; top: 10px; left: 10px; color: white; font-family: monospace; background: rgba(0,0,0,0.4); padding: 5px 10px; border-radius: 8px; }
</style>
</head>
<body>
<div id="debug">Initializing WebGL...</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/examples/js/controls/OrbitControls.js"></script>
<script>
try {
    // WebGL Support check
    if (!window.WebGLRenderingContext) {
        document.getElementById('debug').innerText = "❌ WebGL not supported in this browser/environment.";
    } else {
        const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x000000, 1);
        document.body.appendChild(renderer.domElement);

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 40;

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Lighting
        const light = new THREE.PointLight(0xffffff, 1.2);
        light.position.set(10, 10, 10);
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040));

        // Nodes (simulate cosmic lattice)
        const nodes = [];
        for (let i=0; i<100; i++) {
            const geo = new THREE.SphereGeometry(0.5, 8, 8);
            const mat = new THREE.MeshStandardMaterial({color: new THREE.Color(`hsl(${Math.random()*360},100%,50%)`)});
            const sphere = new THREE.Mesh(geo, mat);
            sphere.position.set((Math.random()-0.5)*50, (Math.random()-0.5)*50, (Math.random()-0.5)*50);
            scene.add(sphere);
            nodes.push(sphere);
        }

        let t = 0;
        const animate = function () {
            requestAnimationFrame(animate);
            t += 0.01;
            nodes.forEach((s, i) => {
                s.scale.setScalar(1 + 0.3 * Math.sin(t + i));
                s.material.color.setHSL((Math.sin(t + i) + 1) / 2, 1, 0.5);
            });
            controls.update();
            renderer.render(scene, camera);
        };

        animate();
        document.getElementById('debug').innerText = "✅ WebGL Initialized Successfully.";
    }
} catch (err) {
    document.getElementById('debug').innerText = "⚠️ Error: " + err.message;
    console.error(err);
}
</script>
</body>
</html>
"""

components.html(html_code, height=800, width=1200, scrolling=False)
