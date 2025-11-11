import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Fractal Conscious Cosmos", layout="wide")

st.title("🌌 Fractal Conscious Cosmos — 3D Visualizer (OrbitControls Fixed)")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fractal Conscious Cosmos — 3D Viewer</title>
<style>
  body { margin: 0; overflow: hidden; background-color: black; }
  #debug { position: absolute; top: 10px; left: 10px; color: white; 
           font-family: monospace; background: rgba(0,0,0,0.4); 
           padding: 5px 10px; border-radius: 8px; z-index: 999; }
</style>
</head>
<body>
<div id="debug">Initializing WebGL...</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>
<script>
// === INLINE ORBIT CONTROLS ===
THREE.OrbitControls = function (object, domElement) {
    this.object = object;
    this.domElement = domElement;
    this.enabled = true;
    this.target = new THREE.Vector3();
    this.rotateSpeed = 1.0;
    this.zoomSpeed = 1.2;
    this.minDistance = 1;
    this.maxDistance = 2000;
    const scope = this;
    function onMouseMove(event) {
        if (!scope.enabled) return;
        if (event.buttons === 1) {
            const movementX = event.movementX || 0;
            const movementY = event.movementY || 0;
            scope.object.rotation.y -= movementX * 0.005 * scope.rotateSpeed;
            scope.object.rotation.x -= movementY * 0.005 * scope.rotateSpeed;
        }
    }
    function onWheel(event) {
        if (!scope.enabled) return;
        scope.object.position.z += event.deltaY * 0.01 * scope.zoomSpeed;
    }
    domElement.addEventListener('mousemove', onMouseMove, false);
    domElement.addEventListener('wheel', onWheel, false);
};
// === END INLINE ORBIT CONTROLS ===

try {
    if (!window.WebGLRenderingContext) {
        document.getElementById('debug').innerText = "❌ WebGL not supported.";
    } else {
        const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x000000, 1);
        document.body.appendChild(renderer.domElement);

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 40;

        const controls = new THREE.OrbitControls(camera, renderer.domElement);

        const light = new THREE.PointLight(0xffffff, 1.2);
        light.position.set(10, 10, 10);
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040));

        const nodes = [];
        for (let i=0; i<100; i++) {
            const geo = new THREE.SphereGeometry(0.5, 8, 8);
            const mat = new THREE.MeshStandardMaterial({color: new THREE.Color(`hsl(${Math.random()*360},100%,50%)`)});
            const s = new THREE.Mesh(geo, mat);
            s.position.set((Math.random()-0.5)*50, (Math.random()-0.5)*50, (Math.random()-0.5)*50);
            scene.add(s);
            nodes.push(s);
        }

        let t = 0;
        function animate() {
            requestAnimationFrame(animate);
            t += 0.01;
            nodes.forEach((s, i) => {
                s.scale.setScalar(1 + 0.3 * Math.sin(t + i));
                s.material.color.setHSL((Math.sin(t + i) + 1)/2, 1, 0.5);
            });
            renderer.render(scene, camera);
        }

        animate();
        document.getElementById('debug').innerText = "✅ WebGL + Controls OK.";
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
