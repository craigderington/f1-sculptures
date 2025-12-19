/**
 * Three.js Scene Manager for F1 Sculpture Rendering
 * Handles 3D scene setup, sculpture rendering, and camera controls
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

class SceneManager {
    constructor(containerId) {
        this.containerId = containerId;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.sculptureGroup = null;
        this.animationId = null;

        this.init();
    }

    /**
     * Initialize Three.js scene
     */
    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);
        this.scene.fog = new THREE.Fog(0x0a0a0a, 200, 500);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            60,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(150, 100, 150);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(this.renderer.domElement);

        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxDistance = 400;
        this.controls.minDistance = 50;

        // Lights
        this.setupLights();

        // Grid helper
        const gridHelper = new THREE.GridHelper(400, 40, 0x333333, 0x1a1a1a);
        this.scene.add(gridHelper);

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());

        // Start animation loop
        this.animate();

        console.log('Three.js scene initialized');
    }

    /**
     * Setup scene lighting
     */
    setupLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 2);
        this.scene.add(ambientLight);

        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(100, 100, 50);
        this.scene.add(directionalLight);

        // Accent back light (theme color)
        const backLight = new THREE.DirectionalLight(0xe94560, 0.5);
        backLight.position.set(-100, 50, -50);
        this.scene.add(backLight);
    }

    /**
     * Build sculpture from telemetry data
     */
    buildSculpture(sculptureData) {
        console.log('Building sculpture with', sculptureData.vertices.length, 'vertices');

        // Remove existing sculpture
        if (this.sculptureGroup) {
            this.scene.remove(this.sculptureGroup);
            this.disposeSculpture();
        }

        this.sculptureGroup = new THREE.Group();

        const vertices = sculptureData.vertices;
        const colors = sculptureData.colors;

        // Create tube geometry along the path
        const path = new THREE.CurvePath();

        for (let i = 0; i < vertices.length - 1; i++) {
            const v1 = new THREE.Vector3(vertices[i].x, vertices[i].y, vertices[i].z);
            const v2 = new THREE.Vector3(vertices[i + 1].x, vertices[i + 1].y, vertices[i + 1].z);
            path.add(new THREE.LineCurve3(v1, v2));
        }

        // Create tube
        const tubeGeometry = new THREE.TubeGeometry(path, vertices.length, 1, 8, false);

        // Create color attribute for tube
        const tubeColors = new Float32Array(tubeGeometry.attributes.position.count * 3);
        const posCount = tubeGeometry.attributes.position.count;
        const segmentCount = vertices.length;

        for (let i = 0; i < posCount; i++) {
            const segmentIndex = Math.floor((i / posCount) * segmentCount);
            const color = colors[Math.min(segmentIndex, colors.length - 1)];
            tubeColors[i * 3] = color.r;
            tubeColors[i * 3 + 1] = color.g;
            tubeColors[i * 3 + 2] = color.b;
        }

        tubeGeometry.setAttribute('color', new THREE.BufferAttribute(tubeColors, 3));

        // Material with vertex colors
        const material = new THREE.MeshPhongMaterial({
            vertexColors: true,
            shininess: 60,
            emissive: 0x111111
        });

        const mesh = new THREE.Mesh(tubeGeometry, material);
        this.sculptureGroup.add(mesh);

        // Add ground shadow (flat projection)
        const shadowGeometry = new THREE.BufferGeometry();
        const shadowPositions = [];

        for (let i = 0; i < vertices.length; i++) {
            shadowPositions.push(vertices[i].x, 0, vertices[i].y);
        }

        shadowGeometry.setAttribute('position', new THREE.Float32BufferAttribute(shadowPositions, 3));

        const shadowMaterial = new THREE.LineBasicMaterial({
            color: 0x333333,
            transparent: true,
            opacity: 0.3
        });

        const shadowLine = new THREE.Line(shadowGeometry, shadowMaterial);
        this.sculptureGroup.add(shadowLine);

        this.scene.add(this.sculptureGroup);

        console.log('Sculpture built successfully');
    }

    /**
     * Dispose of current sculpture to free memory
     */
    disposeSculpture() {
        if (!this.sculptureGroup) return;

        this.sculptureGroup.traverse((object) => {
            if (object.geometry) {
                object.geometry.dispose();
            }
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });

        this.sculptureGroup = null;
    }

    /**
     * Reset camera to default position
     */
    resetCamera() {
        this.camera.position.set(150, 100, 150);
        this.controls.target.set(0, 0, 0);
        this.controls.update();
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }

    /**
     * Animation loop
     */
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Clean up and dispose resources
     */
    dispose() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }

        this.disposeSculpture();

        if (this.renderer) {
            this.renderer.dispose();
        }

        if (this.controls) {
            this.controls.dispose();
        }
    }
}

export default SceneManager;
