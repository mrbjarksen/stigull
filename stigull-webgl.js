window.onload = () => {
    scene.initialize(4, 8);
    scene.render();
    window.addEventListener("keydown", event => {
        if (event.code === "Space") {
            scene.ready();
            scene.animate();
        }
    });
    window.addEventListener("resize", event => { scene.resizeCanvas(); scene.render(); });
};

// ---- Scene and Animation ---- //

const scene = {
    initialize: (baseN, maxN) => {
        scene.baseN = baseN, scene.maxN = maxN;

        const [gl, program, canvas] = setupWebGL();
        scene.gl = gl, scene.program = program, scene.canvas = canvas;

        const maxTri = sierpinski(maxN);
        const overTri = sierpinski(baseN, 2**(maxN-baseN));

        const coordBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, coordBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(grid.coords), gl.STATIC_DRAW);

        const indexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
        gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array([...maxTri, ...overTri]), gl.STATIC_DRAW);

        const pos = gl.getAttribLocation(program, "pos");
        gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
        gl.enableVertexAttribArray(pos);

        const shape = gl.getUniformLocation(program, "shape");
        gl.uniformMatrix2fv(shape, false, shapeMatrix());

        let count = overTri.length, offset = 0, width = 2**baseN;
        scene.tiers = [];
        while (count < maxTri.length) {
            scene.tiers.push({count: count, offset: 2*offset, width: width});
            offset += count;
            count = 2 * offset;
            width *= 2;
        }

        scene.overlay = {count: overTri.length, offset: 2*offset}

        scene.text = document.getElementById("stigull-text");
        scene.oint = document.getElementById("stigull-oint");

        scene.ready();
    },
    resizeCanvas: () => {
        const canvas = scene.canvas;
        const displayWidth = canvas.clientWidth;
        const displayHeight = canvas.clientHeight

        // const dpr = window.devicePixelRatio || 1;
        // const displayWidth = Math.floor(canvas.clientWidth * dpr);
        // const displayHeight = Math.floor(canvas.clientHeight * dpr);

        if (canvas.width !== displayWidth || canvas.height !== displayHeight) {
            canvas.width = displayWidth;
            canvas.height = displayHeight;
            scene.gl.viewport(0, 0, canvas.width, canvas.height);
            uniforms.set("aspectRatio", canvas.width/canvas.height)
        }
    },
    ready: () => {
        uniforms.set("width", 2**scene.baseN);
        uniforms.set("overlayOpacity", 0);

        scene.animationQueue = [];
        scene.animationQueue.push(new Animation({
            to: {width: 2**scene.maxN},
            duration: 3,
        }));
        scene.animationQueue.push(new Animation({
            to: {overlayOpacity: 1},
        }));
        scene._lastTime = 0;
        
        scene.render();
    },
    render: () => {
        scene.resizeCanvas();
        scene.gl.clear(scene.gl.COLOR_BUFFER_BIT);
        if (uniforms.overlayOpacity.value < 1) {
            uniforms.set("isOverlay", 0);
            for (tier of scene.tiers) {
                if (tier.width >= 2*uniforms.width.value) break;
                uniforms.set("tierWidth", tier.width);
                scene.gl.drawElements(scene.gl.TRIANGLES, tier.count, scene.gl.UNSIGNED_SHORT, tier.offset);
            }
        }
        uniforms.set("isOverlay", 1);
        scene.gl.drawElements(scene.gl.TRIANGLES, scene.overlay.count, scene.gl.UNSIGNED_SHORT, scene.overlay.offset);

        // scene.text.style.width = 
    },
    animationQueue: [],
    advanceAnimationQueue: (dt) => {
        if (scene.animationQueue.length === 0) return;
        let current = scene.animationQueue[0];
        current.advance(dt);
        const excess = current.timer - current.duration;
        if (excess > 0) {
            scene.animationQueue.shift()
            scene.advanceAnimationQueue(excess);
        }
    },
    animate: (dt) => {
        if (dt !== undefined) {
            if (scene.animationQueue.length === 0) return;
            scene.advanceAnimationQueue(dt);
        }
        scene.render();
        window.requestAnimationFrame(scene._animateWrapper);
    },
    _lastTime: 0,
    _animateWrapper: (timestamp) => {
        const dt = scene._lastTime === 0 ? 0 : (timestamp - scene._lastTime) / 1000;
        scene._lastTime = timestamp;
        scene.animate(dt);
    }
};

const uniforms = {
    set: function(name, value) {
        if (this[name] === undefined) {
            this[name] = {
                location: scene.gl.getUniformLocation(scene.program, name)
            };
        }
        this[name].value = value;
        scene.gl.uniform1f(this[name].location, value);
    },
}

const confine = (x) => x < 0 ? 0 : x > 1 ? 1 : x;
const sigmoid = (x) => 1 / (1 + Math.exp(-x)) ;
const smooth = (t, inflection = 10) => {
    if (t < 0) return 0;
    if (t > 1) return 1;
    const err = sigmoid(-inflection/2);
    return confine((sigmoid(inflection*(t - 1/2)) - err) / (1 - 2*err));
};

class Animation {
    constructor(args) {
        this.to = args.to || {};
        this.by = args.by || {};
        this.from = {}
        for (const uniform in this.to)
            this.from[uniform] = uniforms[uniform].value;
        for (const uniform in this.by)
            this.from[uniform] = uniforms[uniform].value;

        this.timer = 0;
        this.duration = args.duration === undefined ? 1 : args.duration;

        this.interpolation = args.interpolation === undefined ? smooth : args.interpolation;
    }

    advance(dt) {
        this.timer += dt;
        const timeProportion = confine(this.timer/this.duration)
        const alpha = this.interpolation(timeProportion);
        for (const uniform in this.to) {
            const value = this.from[uniform]*(1 - alpha) + this.to[uniform]*alpha;
            uniforms.set(uniform, value);
        }
        for (const uniform in this.by) {
            const mult = (1 - alpha) + this.by[uniform]*alpha;
            const value = this.from[uniform] * mult;
            uniforms.set(uniform, value);
        }
    }
}

// ---- Coordinates and Data ---- //

const grid = {
    coords: [0, 0],
    depth: 0,
    extend: function(n) {
        for (let d = this.depth + 1; d <= n; d++) {
            for (let x = 0; x <= d; x++) this.coords.push(x, d - x);
            this.depth = n;
        }
    },
    index: function(x, y) {
        const d = x + y;
        if (d > this.depth) this.extend(d);
        return (d+1)*(d+2)/2 - y - 1;
    },
    triangle: function(x, y, size) {
        return [
            this.index(x, y),
            this.index(x + size, y),
            this.index(x, y + size),
        ];
    },
};

const sierpinski = (n, size = 1, x = 0, y = 0) => {
    if (n === 0) return grid.triangle(x, y, size);
    const mid = size * 2**(n-1);
    return [
        ...sierpinski(n - 1, size, x, y),
        ...sierpinski(n - 1, size, x + mid, y),
        ...sierpinski(n - 1, size, x, y + mid),
    ];
};

const shapeMatrix = () => {
    // Magic numbers :(
    const sc = 0.05,
          xmin = 0.18 - sc,
          xmax = 1 - 0.18 + sc;
          ymin = 0.1, 
          ymax = 0.7928 + 2.46*sc;
    return new Float32Array([
        1, 0,
        1/2, -(ymax-ymin)/(xmax-xmin),
    ]);
};

// ---- WebGL ---- //

const setupWebGL = () => {
    const canvas = document.getElementById("gl-canvas");

    const gl = canvas.getContext("webgl");

    const vshader = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vshader, document.getElementById("vertex-shader").text);
    gl.compileShader(vshader);

    if (!gl.getShaderParameter(vshader, gl.COMPILE_STATUS)) alert(gl.getShaderInfoLog(vshader));

    const fshader = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fshader, document.getElementById("fragment-shader").text);
    gl.compileShader(fshader);

    if (!gl.getShaderParameter(fshader, gl.COMPILE_STATUS)) alert(gl.getShaderInfoLog(fshader));

    const program = gl.createProgram();
    gl.attachShader(program, vshader);
    gl.attachShader(program, fshader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) alert(gl.getProgramInfoLog(fshader));

    gl.useProgram(program);

    gl.clearColor(0, 0, 0, 0);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    return [gl, program, canvas];
};
