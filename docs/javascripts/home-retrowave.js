(() => {
    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    const pageUrl = new URL(canonical || window.location.href, window.location.href);
    const normalizedPath = pageUrl.pathname.replace(/\/index\.html$/, "/");
    const isHomePage = /^\/(?:android-dev-handbook\/)?(?:(?:en|ru)\/)?$/.test(normalizedPath);

    if (!isHomePage || document.querySelector(".handbook-retrowave-layer")) {
        return;
    }

    document.body.classList.add("handbook-retrowave-home");

    const layer = document.createElement("div");
    layer.className = "handbook-retrowave-layer";
    layer.setAttribute("aria-hidden", "true");

    const staticCanvas = document.createElement("canvas");
    staticCanvas.className = "handbook-retrowave-canvas handbook-retrowave-canvas--static";

    const canvas = document.createElement("canvas");
    canvas.className = "handbook-retrowave-canvas handbook-retrowave-canvas--dynamic";

    layer.append(staticCanvas, canvas);
    document.body.prepend(layer);

    const context = canvas.getContext("2d", { alpha: true });
    const staticContext = staticCanvas.getContext("2d", { alpha: true });
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let width = 0;
    let height = 0;
    let pixelRatio = 1;
    let compactViewport = false;
    let portraitScene = false;
    let depths = [];
    let frameId = 0;
    let frameAccumulator = 0;
    let lastAnimationTime = 0;
    let lastFrameTime = 0;
    let resizeFrame = 0;
    let previousScrollY = 0;
    let smoothedScrollVelocity = 0;
    const depthMotionBias = 0.2;
    const scrollVelocityScale = 1200;
    const maximumScrollBoost = 1.2;

    const geometry = {
        near: 1.35,
        far: 54,
        speed: 2.55,
        depthLines: 24,
        lanes: 19,
        targetFrameTime: 1000 / 90
    };

    function updateGeometry() {
        geometry.depthLines = compactViewport ? 16 : 24;
        geometry.lanes = compactViewport ? 11 : 19;
        geometry.speed = compactViewport ? 1.92 : 2.55;
        geometry.targetFrameTime = 1000 / (compactViewport ? 60 : 90);

        const depthRange = geometry.far - geometry.near;
        depths = Array.from(
            { length: geometry.depthLines },
            (_, index) => geometry.near + (depthRange * index) / geometry.depthLines
        );
    }

    function resizeCanvas() {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const nextPortraitScene = viewportHeight / viewportWidth > 1.1;

        layer.classList.toggle("handbook-retrowave-layer--portrait", nextPortraitScene);
        document.body.classList.toggle("handbook-retrowave-portrait", nextPortraitScene);

        const nextWidth = Math.round(canvas.clientWidth);
        const nextHeight = Math.round(canvas.clientHeight);
        const nextCompactViewport = Math.min(nextWidth, nextHeight) < 768;
        const nextPixelRatio = Math.min(
            window.devicePixelRatio || 1,
            nextCompactViewport ? 1 : 1.25
        );

        if (
            nextWidth === width
            && nextHeight === height
            && nextPixelRatio === pixelRatio
            && nextCompactViewport === compactViewport
            && nextPortraitScene === portraitScene
        ) {
            return;
        }

        width = nextWidth;
        height = nextHeight;
        pixelRatio = nextPixelRatio;
        compactViewport = nextCompactViewport;
        portraitScene = nextPortraitScene;
        canvas.width = Math.round(width * pixelRatio);
        canvas.height = Math.round(height * pixelRatio);
        staticCanvas.width = canvas.width;
        staticCanvas.height = canvas.height;
        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
        staticContext.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
        updateGeometry();
        rebuildStaticLayer();
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
        const perspectiveProgress = Math.max(
            0,
            Math.min(1, (1 / depth - farInverse) / (nearInverse - farInverse))
        );

        return perspectiveProgress
            + perspectiveProgress * (1 - perspectiveProgress) * depthMotionBias;
    }

    function gridMetrics() {
        const horizon = height * 0.5;
        const gap = Math.max(44, Math.min(92, height * 0.095));
        const virtualWidth = Math.max(width, height * (16 / 9));
        return {
            centerX: width * 0.5,
            horizon,
            gap,
            topHorizon: horizon - gap * 0.5,
            bottomHorizon: horizon + gap * 0.5,
            horizonSpan: width,
            edgeSpan: virtualWidth * 2
        };
    }

    function configureGridStroke(target, palette, glow) {
        target.strokeStyle = `rgba(${palette.line}, ${glow ? palette.glowAlpha : palette.sharpAlpha})`;
        target.lineWidth = glow ? 3.2 : 0.72;
        target.shadowColor = glow ? `rgba(${palette.line}, .72)` : "transparent";
        target.shadowBlur = glow ? 10 : 0;
    }

    function drawPerspectivePass(target, palette, glow) {
        const metrics = gridMetrics();
        target.save();
        configureGridStroke(target, palette, glow);
        target.beginPath();

        for (let index = 0; index < geometry.lanes; index += 1) {
            const lane = geometry.lanes === 1 ? 0 : index / (geometry.lanes - 1);
            const edgeX = metrics.centerX + (lane - 0.5) * metrics.edgeSpan;
            const horizonX = metrics.centerX + (lane - 0.5) * metrics.horizonSpan;

            target.moveTo(horizonX, metrics.topHorizon);
            target.lineTo(edgeX, 0);
            target.moveTo(horizonX, metrics.bottomHorizon);
            target.lineTo(edgeX, height);
        }

        target.stroke();
        target.restore();
    }

    function drawDepthPass(palette, glow) {
        const metrics = gridMetrics();
        const topHeight = metrics.topHorizon;
        const bottomHeight = height - metrics.bottomHorizon;
        const horizonHalfWidth = metrics.horizonSpan * 0.5;
        const edgeHalfWidth = metrics.edgeSpan * 0.5;

        context.save();
        configureGridStroke(context, palette, glow);
        context.beginPath();

        for (const depth of depths) {
            const progress = projectDepth(depth);
            const halfWidth = horizonHalfWidth + (edgeHalfWidth - horizonHalfWidth) * progress;

            context.moveTo(
                metrics.centerX - halfWidth,
                metrics.bottomHorizon + bottomHeight * progress
            );
            context.lineTo(
                metrics.centerX + halfWidth,
                metrics.bottomHorizon + bottomHeight * progress
            );
            context.moveTo(
                metrics.centerX - halfWidth,
                metrics.topHorizon - topHeight * progress
            );
            context.lineTo(
                metrics.centerX + halfWidth,
                metrics.topHorizon - topHeight * progress
            );
        }

        context.stroke();
        context.restore();
    }

    function drawHorizon(target, palette) {
        const metrics = gridMetrics();
        const gradient = target.createLinearGradient(
            0,
            metrics.horizon - metrics.gap,
            0,
            metrics.horizon + metrics.gap
        );

        gradient.addColorStop(0, `rgba(${palette.horizon}, 0)`);
        gradient.addColorStop(0.25, `rgba(${palette.horizon}, .14)`);
        gradient.addColorStop(0.48, `rgba(${palette.horizon}, .05)`);
        gradient.addColorStop(0.52, `rgba(${palette.horizon}, .05)`);
        gradient.addColorStop(0.75, `rgba(${palette.horizon}, .14)`);
        gradient.addColorStop(1, `rgba(${palette.horizon}, 0)`);
        target.fillStyle = gradient;
        target.fillRect(0, metrics.horizon - metrics.gap, width, metrics.gap * 2);

        target.save();
        target.strokeStyle = `rgba(${palette.horizon}, .58)`;
        target.lineWidth = 1;
        target.shadowColor = `rgba(${palette.horizon}, .8)`;
        target.shadowBlur = 14;
        target.beginPath();
        target.moveTo(0, metrics.topHorizon);
        target.lineTo(width, metrics.topHorizon);
        target.moveTo(0, metrics.bottomHorizon);
        target.lineTo(width, metrics.bottomHorizon);
        target.stroke();
        target.restore();
    }

    function rebuildStaticLayer() {
        staticContext.clearRect(0, 0, width, height);
        const palette = currentPalette();
        drawHorizon(staticContext, palette);
        drawPerspectivePass(staticContext, palette, true);
        drawPerspectivePass(staticContext, palette, false);
    }

    function drawGrid() {
        context.clearRect(0, 0, width, height);
        const palette = currentPalette();
        drawDepthPass(palette, true);
        drawDepthPass(palette, false);
    }

    function readScrollPosition() {
        return Math.max(
            0,
            document.scrollingElement?.scrollTop ?? window.scrollY ?? 0
        );
    }

    function animate(timestamp) {
        frameId = 0;

        if (document.hidden || reducedMotion.matches) {
            return;
        }

        frameAccumulator += Math.min(timestamp - lastAnimationTime, 50);
        lastAnimationTime = timestamp;

        if (frameAccumulator >= geometry.targetFrameTime) {
            const deltaSeconds = Math.min((timestamp - lastFrameTime) / 1000, 0.05);
            frameAccumulator %= geometry.targetFrameTime;
            lastFrameTime = timestamp;
            const depthRange = geometry.far - geometry.near;
            const scrollY = readScrollPosition();
            const scrollVelocity = Math.abs(scrollY - previousScrollY) / deltaSeconds;
            const scrollResponse = Math.min(1, deltaSeconds * 9);
            previousScrollY = scrollY;
            smoothedScrollVelocity += (
                scrollVelocity - smoothedScrollVelocity
            ) * scrollResponse;
            const scrollBoost = Math.min(
                smoothedScrollVelocity / scrollVelocityScale,
                maximumScrollBoost
            );
            const effectiveSpeed = geometry.speed * (1 + scrollBoost);

            for (let index = 0; index < depths.length; index += 1) {
                const nextDepth = depths[index] - effectiveSpeed * deltaSeconds;
                depths[index] = nextDepth <= geometry.near ? nextDepth + depthRange : nextDepth;
            }

            drawGrid();
        }

        frameId = window.requestAnimationFrame(animate);
    }

    function stopAnimation() {
        window.cancelAnimationFrame(frameId);
        frameId = 0;
    }

    function startAnimation() {
        if (frameId || document.hidden || reducedMotion.matches) {
            return;
        }

        const startTime = performance.now();
        frameAccumulator = 0;
        lastAnimationTime = startTime;
        lastFrameTime = startTime;
        previousScrollY = readScrollPosition();
        smoothedScrollVelocity = 0;
        frameId = window.requestAnimationFrame(animate);
    }

    function handleResize() {
        window.cancelAnimationFrame(resizeFrame);
        resizeFrame = window.requestAnimationFrame(resizeCanvas);
    }

    function handleMotionPreference() {
        stopAnimation();
        drawGrid();
        startAnimation();
    }

    function handleVisibilityChange() {
        if (document.hidden) {
            stopAnimation();
            return;
        }

        startAnimation();
    }

    function handlePaletteChange() {
        rebuildStaticLayer();
        drawGrid();
    }

    window.addEventListener("resize", handleResize, { passive: true });
    document.addEventListener("visibilitychange", handleVisibilityChange);
    reducedMotion.addEventListener("change", handleMotionPreference);

    const paletteObserver = new MutationObserver(handlePaletteChange);
    paletteObserver.observe(document.body, {
        attributes: true,
        attributeFilter: ["data-md-color-scheme"]
    });

    resizeCanvas();
    handleMotionPreference();
})();
