const stage = document.querySelector("#stage");
const canvas = document.querySelector("#fireworksCanvas");
const exitButton = document.querySelector("#exitButton");
const context = canvas.getContext("2d");

let width = 0;
let height = 0;
let rockets = [];
let particles = [];
let spawnTimer = 0;
let lastTime = performance.now();
let isClosed = false;

const colors = [
  [255, 116, 142],
  [255, 210, 92],
  [120, 220, 255],
  [183, 151, 255],
  [145, 239, 191],
  [255, 160, 220]
];

function randomBetween(min, max) {
  return Math.random() * (max - min) + min;
}

function resizeCanvas() {
  const rect = stage.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;

  width = rect.width;
  height = rect.height;
  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
}

class Rocket {
  constructor() {
    this.x = randomBetween(width * 0.12, width * 0.88);
    this.y = height + 20;
    this.targetY = randomBetween(height * 0.12, height * 0.48);
    this.vx = randomBetween(-0.7, 0.7);
    this.vy = randomBetween(-10.5, -8);
    this.color = colors[Math.floor(Math.random() * colors.length)];
    this.trail = [];
  }

  update() {
    this.trail.push({ x: this.x, y: this.y });

    if (this.trail.length > 14) {
      this.trail.shift();
    }

    this.x += this.vx;
    this.y += this.vy;
    this.vy += 0.08;
  }

  draw() {
    this.trail.forEach((point, index) => {
      const alpha = (index + 1) / this.trail.length;
      context.fillStyle = `rgba(${this.color.join(",")},${alpha * 0.7})`;
      context.beginPath();
      context.arc(point.x, point.y, 2, 0, Math.PI * 2);
      context.fill();
    });

    context.fillStyle = `rgb(${this.color.join(",")})`;
    context.beginPath();
    context.arc(this.x, this.y, 4, 0, Math.PI * 2);
    context.fill();
  }

  shouldExplode() {
    return this.y <= this.targetY || this.vy >= -1.5;
  }
}

class Particle {
  constructor(x, y, color) {
    const angle = randomBetween(0, Math.PI * 2);
    const speed = randomBetween(2.2, 7.2);

    this.x = x;
    this.y = y;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed;
    this.color = color;
    this.life = Math.floor(randomBetween(55, 95));
    this.maxLife = this.life;
    this.radius = randomBetween(1.8, 3.8);
    this.gravity = randomBetween(0.035, 0.075);
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;
    this.vx *= 0.992;
    this.life -= 1;
  }

  draw() {
    const alpha = Math.max(this.life / this.maxLife, 0);
    const color = this.color.join(",");

    context.fillStyle = `rgba(${color},${alpha * 0.22})`;
    context.beginPath();
    context.arc(this.x, this.y, this.radius * 5, 0, Math.PI * 2);
    context.fill();

    context.fillStyle = `rgba(${color},${alpha})`;
    context.beginPath();
    context.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    context.fill();
  }
}

function explode(x, y, baseColor) {
  const palette = [
    baseColor,
    [255, 245, 180],
    [255, 185, 220],
    [155, 235, 255],
    [190, 255, 205]
  ];

  for (let index = 0; index < randomBetween(90, 145); index += 1) {
    const color = palette[Math.floor(Math.random() * palette.length)];
    particles.push(new Particle(x, y, color));
  }
}

function animate(now) {
  if (isClosed) {
    return;
  }

  const delta = (now - lastTime) / 1000;
  lastTime = now;
  context.clearRect(0, 0, width, height);

  spawnTimer -= delta;
  if (spawnTimer <= 0) {
    rockets.push(new Rocket());
    spawnTimer = randomBetween(0.28, 0.75);
  }

  rockets = rockets.filter((rocket) => {
    rocket.update();
    rocket.draw();

    if (rocket.shouldExplode()) {
      explode(rocket.x, rocket.y, rocket.color);
      return false;
    }

    return true;
  });

  particles = particles.filter((particle) => {
    particle.update();
    particle.draw();
    return particle.life > 0;
  });

  requestAnimationFrame(animate);
}

// Click vao anh tao them mot chum phao hoa, tru nut EXIT.
stage.addEventListener("click", (event) => {
  if (event.target === exitButton || isClosed) {
    return;
  }

  const rect = stage.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  const color = colors[Math.floor(Math.random() * colors.length)];
  explode(x, y, color);
});

exitButton.addEventListener("click", () => {
  isClosed = true;
  stage.classList.add("closed");
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    isClosed = true;
    stage.classList.add("closed");
  }
});

window.addEventListener("resize", resizeCanvas);

resizeCanvas();
requestAnimationFrame(animate);
