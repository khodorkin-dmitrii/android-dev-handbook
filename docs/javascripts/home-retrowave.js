(() => {
    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    const pageUrl = new URL(canonical || window.location.href, window.location.href);
    const normalizedPath = pageUrl.pathname.replace(/\/index\.html$/, "/");
    const isHomePage = /^\/(?:android-dev-handbook\/)?(?:(?:en|ru)\/)?$/.test(normalizedPath);

    if (!isHomePage || document.querySelector(".handbook-retrowave-canvas")) {
        return;
    }

    document.body.classList.add("handbook-retrowave-home");

    const canvas = document.createElement("canvas");
    canvas.className = "handbook-retrowave-canvas";
    canvas.setAttribute("aria-hidden", "true");
    document.body.prepend(canvas);

    const context = canvas.getContext("2d", { alpha: true });
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let width = 0;
    let height = 0;
    let pixelRatio = 1;
    let depths = [];
    let frameId = 0;
    let lastFrameTime = 0;
    let resizeFrame = 0;

    const geometry = {
        near: 1.35,
        far: 54,
        speed: 4.25,
        depthLines: 20,
        lanes: 21,
        targetFrameTime: 1000 / 45
    };

    function updateGeometry() {
        const compact = width < 768;
        geometry.depthLines = compact ? 13 : 20;
        geometry.lanes = compact ? 13 : 21;
        geometry.speed = compact ? 3.2 : 4.25;
        geometry.targetFrameTime = 1000 / (compact ? 30 : 45);

        const depthRange = geometry.far - geometry.near;
        depths = Array.from(
            { length: geometry.depthLines },
            (_, index) => geometry.near + (depthRange * index) / geometry.depthLines
        );
    }

    function resizeCanvas() {
        width = window.innerWidth;
        height = window.innerHeight;
        pixelRatio = Math.min(window.devicePixelRatio || 1, 1.5);
        canvas.width = Math.round(width * pixelRatio);
        canvas.height = Math.round(height * pixelRatio);
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
        updateGeometry();
        drawGrid();
    }

    function currentPalette() {
        const dark = document.body.getAttribute("data-md-color-scheme") === "slate";
        return dark
            ? {
                line: "236, 65, 255",
                horizon: "255, 47, 210",
                sharpAlpha: 0.54,
                glowAlpha: 0.16
            }
            : {
                line: "147, 43, 196",
                horizon: "211, 52, 170",
                sharpAlpha: 0.32,
                glowAlpha: 0.09
            };
    }

    function projectDepth(depth) {
        const nearInverse = 1 / geometry.near;
        const farInverse = 1 / geometry.far;
        return Math.max(
            0,
            Math.min(1, (1 / depth - farInverse) / (nearInverse - farInverse))
        );
    }

    function drawGridPass(palette, glow) {
        const horizon = height * 0.5;
        const gap = Math.max(44, Math.min(92, height * 0.095));
        const topHorizon = horizon - gap * 0.5;
        const bottomHorizon = horizon + gap * 0.5;
        const vanishingX = width * 0.5;
        const topHeight = topHorizon;
        const bottomHeight = height - bottomHorizon;
        const outerMargin = width * 0.035;

        context.save();
        context.strokeStyle = `rgba(${palette.line}, ${glow ? palette.glowAlpha : palette.sharpAlpha})`;
        context.lineWidth = glow ? 3.4 : 0.72;
        context.shadowColor = glow ? `rgba(${palette.line}, .8)` : "transparent";
        context.shadowBlur = glow ? 13 : 0;

        for (let index = 0; index < geometry.lanes; index += 1) {
            const lane = geometry.lanes === 1 ? 0 : index / (geometry.lanes - 1);
            const edgeX = outerMargin + lane * (width - outerMargin * 2);

            context.beginPath();
            context.moveTo(vanishingX, topHorizon);
            context.lineTo(edgeX, 0);
            context.stroke();

            context.beginPath();
            context.moveTo(vanishingX, bottomHorizon);
            context.lineTo(edgeX, height);
            context.stroke();
        }

        depths.forEach((depth) => {
            const progress = projectDepth(depth);
            const halfWidth = width * (0.025 + progress * 0.56);

            context.beginPath();
            context.moveTo(vanishingX - halfWidth, bottomHorizon + bottomHeight * progress);
            context.lineTo(vanishingX + halfWidth, bottomHorizon + bottomHeight * progress);
            context.stroke();

            context.beginPath();
            context.moveTo(vanishingX - halfWidth, topHorizon - topHeight * progress);
            context.lineTo(vanishingX + halfWidth, topHorizon - topHeight * progress);
            context.stroke();
        });

        context.restore();
    }

    function drawHorizon(palette) {
        const horizon = height * 0.5;
        const gap = Math.max(44, Math.min(92, height * 0.095));
        const gradient = context.createLinearGradient(0, horizon - gap, 0, horizon + gap);

        gradient.addColorStop(0, `rgba(${palette.horizon}, 0)`);
        gradient.addColorStop(0.25, `rgba(${palette.horizon}, .14)`);
        gradient.addColorStop(0.48, `rgba(${palette.horizon}, .05)`);
        gradient.addColorStop(0.52, `rgba(${palette.horizon}, .05)`);
        gradient.addColorStop(0.75, `rgba(${palette.horizon}, .14)`);
        gradient.addColorStop(1, `rgba(${palette.horizon}, 0)`);
        context.fillStyle = gradient;
        context.fillRect(0, horizon - gap, width, gap * 2);

        context.save();
        context.strokeStyle = `rgba(${palette.horizon}, .58)`;
        context.lineWidth = 1;
        context.shadowColor = `rgba(${palette.horizon}, .9)`;
        context.shadowBlur = 18;

        context.beginPath();
        context.moveTo(0, horizon - gap * 0.5);
        context.lineTo(width, horizon - gap * 0.5);
        context.stroke();

        context.beginPath();
        context.moveTo(0, horizon + gap * 0.5);
        context.lineTo(width, horizon + gap * 0.5);
        context.stroke();
        context.restore();
    }

    function drawGrid() {
        context.clearRect(0, 0, width, height);
        const palette = currentPalette();
        drawHorizon(palette);
        drawGridPass(palette, true);
        drawGridPass(palette, false);
    }

    function animate(timestamp) {
        frameId = window.requestAnimationFrame(animate);

        if (document.hidden || timestamp - lastFrameTime < geometry.targetFrameTime) {
            return;
        }

        const deltaSeconds = Math.min((timestamp - lastFrameTime) / 1000, 0.05);
        lastFrameTime = timestamp;
        const depthRange = geometry.far - geometry.near;

        depths = depths.map((depth) => {
            const nextDepth = depth - geometry.speed * deltaSeconds;
            return nextDepth <= geometry.near ? nextDepth + depthRange : nextDepth;
        });

        drawGrid();
    }

    function handleResize() {
        window.cancelAnimationFrame(resizeFrame);
        resizeFrame = window.requestAnimationFrame(resizeCanvas);
    }

    function handleMotionPreference() {
        window.cancelAnimationFrame(frameId);
        frameId = 0;
        lastFrameTime = 0;
        drawGrid();

        if (!reducedMotion.matches) {
            frameId = window.requestAnimationFrame(animate);
        }
    }

    window.addEventListener("resize", handleResize, { passive: true });
    reducedMotion.addEventListener("change", handleMotionPreference);

    const paletteObserver = new MutationObserver(drawGrid);
    paletteObserver.observe(document.body, {
        attributes: true,
        attributeFilter: ["data-md-color-scheme"]
    });

    resizeCanvas();
    handleMotionPreference();
})();
