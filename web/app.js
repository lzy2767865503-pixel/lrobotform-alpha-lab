const translations = {
  en: {
    noticeTitle: "Simulation-only research workspace",
    noticeBody:
      "Generates local synthetic datasets for authorized questionnaire design and Cronbach's Alpha testing. It never submits responses to Google Forms.",
    eyebrow: "QUESTIONNAIRE RELIABILITY LAB",
    intro:
      "Model a pilot dataset, inspect response distributions, and verify whether an ordered scale reaches the selected reliability band before real participant recruitment.",
    scopeData: "Data",
    scopeDataValue: "Synthetic and local",
    scopeNetwork: "Network",
    scopeNetworkValue: "No form submission",
    scopeOwner: "Project owner",
    toolEyebrow: "LOCAL SIMULATOR",
    toolTitle: "Reliability test configuration",
    ready: "Ready",
    running: "Running",
    complete: "Complete",
    responses: "Synthetic responses",
    items: "Ordered scale items",
    targetMin: "Target Alpha minimum",
    targetMax: "Target Alpha maximum",
    seed: "Reproducibility seed",
    distribution: "Non-scale distribution",
    normal: "Normal-shaped",
    normalHelp: "Ordered choices cluster around the centre.",
    uniform: "Uniform",
    uniformHelp: "Each nominal option has equal probability.",
    run: "Run local simulation",
    download: "Download CSV",
    alpha: "Cronbach's Alpha",
    sample: "Sample size",
    attempts: "Calibration passes",
    waitingTitle: "Awaiting simulation",
    waitingBody: "Configure the test and run it locally. No data leaves this browser.",
    passTitle: "Reliability target reached",
    passBody: "The local synthetic pilot falls inside the selected Alpha band.",
    warningTitle: "Best calibration returned",
    warningBody: "The closest local result is shown. Adjust the item count or sample size and run again.",
    distributionTitle: "Aggregate scale distribution",
    emptyChart: "Run a simulation to view the distribution.",
    previewTitle: "Synthetic data preview",
    previewLimit: "First 5 rows",
    previewEmpty: "No dataset",
    previewPrompt: "Run a local simulation to generate preview rows.",
    methodEyebrow: "RESEARCH BOUNDARY",
    methodTitle: "What this public project proves",
    methodOne: "Read-only questionnaire schema normalization.",
    methodTwo: "Reproducible synthetic pilot-data generation.",
    methodThree: "Cronbach's Alpha calibration and distribution reporting.",
    methodFour: "No automated submission to live Google Forms.",
    notAffiliated: "Independent research project; not affiliated with Google.",
    rows: "rows",
  },
  zh: {
    noticeTitle: "仅限本地模拟研究",
    noticeBody:
      "为已获授权的问卷设计与 Cronbach's Alpha 测试生成本地合成数据；本工具不会向 Google Forms 提交回复。",
    eyebrow: "问卷可靠性实验室",
    intro:
      "在招募真实参与者之前，先建立合成试验样本、检查回答分布，并验证有序量表能否达到设定的可靠性区间。",
    scopeData: "数据",
    scopeDataValue: "本地合成数据",
    scopeNetwork: "网络行为",
    scopeNetworkValue: "不提交表单",
    scopeOwner: "项目所有者",
    toolEyebrow: "本地模拟器",
    toolTitle: "可靠性测试参数",
    ready: "准备就绪",
    running: "正在计算",
    complete: "已完成",
    responses: "合成样本数",
    items: "有序量表题数",
    targetMin: "Alpha 目标下限",
    targetMax: "Alpha 目标上限",
    seed: "可复现随机种子",
    distribution: "非量表题分布",
    normal: "近似正态分布",
    normalHelp: "有序选项集中于中间区间。",
    uniform: "均匀分布",
    uniformHelp: "名义选项拥有相同概率。",
    run: "运行本地模拟",
    download: "下载 CSV",
    alpha: "Cronbach's Alpha",
    sample: "样本量",
    attempts: "校准次数",
    waitingTitle: "等待运行",
    waitingBody: "设置参数后在本地运行，数据不会离开浏览器。",
    passTitle: "可靠性目标已达到",
    passBody: "本地合成试验样本位于设定的 Alpha 区间内。",
    warningTitle: "已返回最佳校准结果",
    warningBody: "当前显示最接近目标的本地结果，可调整题数或样本量后重试。",
    distributionTitle: "量表总体分布",
    emptyChart: "运行模拟后查看分布。",
    previewTitle: "合成数据预览",
    previewLimit: "前 5 行",
    previewEmpty: "暂无数据",
    previewPrompt: "运行本地模拟以生成预览。",
    methodEyebrow: "研究边界",
    methodTitle: "这个公开项目证明什么",
    methodOne: "只读式问卷结构标准化。",
    methodTwo: "可复现的合成试验数据生成。",
    methodThree: "Cronbach's Alpha 校准与分布报告。",
    methodFour: "不向真实 Google Forms 自动提交回复。",
    notAffiliated: "独立研究项目，与 Google 无隶属关系。",
    rows: "行",
  },
};

let language = "en";
let currentRows = [];

function mulberry32(seed) {
  return function random() {
    let value = (seed += 0x6d2b79f5);
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function normal(random) {
  const first = Math.max(1e-9, random());
  const second = Math.max(1e-9, random());
  return Math.sqrt(-2 * Math.log(first)) * Math.cos(2 * Math.PI * second);
}

function variance(values) {
  if (values.length < 2) return 0;
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  return (
    values.reduce((sum, value) => sum + (value - mean) ** 2, 0) /
    (values.length - 1)
  );
}

function cronbachAlpha(matrix) {
  if (matrix.length < 2 || matrix[0].length < 2) return null;
  const width = matrix[0].length;
  const itemVariances = Array.from({ length: width }, (_, column) =>
    variance(matrix.map((row) => row[column])),
  );
  const totals = matrix.map((row) => row.reduce((sum, value) => sum + value, 0));
  const totalVariance = variance(totals);
  if (totalVariance <= 0) return null;
  return (width / (width - 1)) * (1 - itemVariances.reduce((a, b) => a + b, 0) / totalVariance);
}

function generateCandidate(responseCount, itemCount, seed, adjustment) {
  const random = mulberry32(seed);
  const loading = Math.min(0.94, Math.max(0.18, adjustment));
  const noise = Math.sqrt(Math.max(0.001, 1 - loading ** 2));
  return Array.from({ length: responseCount }, () => {
    const latent = normal(random);
    return Array.from({ length: itemCount }, (_, index) => {
      const score = loading * latent + noise * normal(random) + ((index % 5) - 2) * 0.06;
      const probability = 1 / (1 + Math.exp(-score));
      return Math.max(1, Math.min(5, Math.round(1 + probability * 4)));
    });
  });
}

function calibrate(responseCount, itemCount, seed, targetMin, targetMax) {
  const target = (targetMin + targetMax) / 2;
  let best = null;
  for (let attempt = 1; attempt <= 120; attempt += 1) {
    const loading = 0.25 + ((attempt - 1) % 50) * 0.014;
    const matrix = generateCandidate(
      responseCount,
      itemCount,
      seed + attempt * 7919,
      loading,
    );
    const alpha = cronbachAlpha(matrix);
    if (!Number.isFinite(alpha)) continue;
    const distance =
      alpha >= targetMin && alpha <= targetMax
        ? 0
        : Math.min(Math.abs(alpha - targetMin), Math.abs(alpha - targetMax));
    const candidate = { matrix, alpha, attempt, distance };
    if (
      !best ||
      distance < best.distance ||
      (distance === best.distance && Math.abs(alpha - target) < Math.abs(best.alpha - target))
    ) {
      best = candidate;
    }
    if (distance === 0 && Math.abs(alpha - target) <= 0.025) break;
  }
  return best;
}

function buildRows(matrix, seed, distribution) {
  return matrix.map((scaleValues, index) => {
    const random = mulberry32(seed + index * 1009);
    const programmeOptions = ["Foundation", "Undergraduate", "Postgraduate"];
    const ageOptions = ["18-20", "21-23", "24-26", "27+"];
    const ageIndex =
      distribution === "normal"
        ? Math.max(0, Math.min(ageOptions.length - 1, Math.round(1.4 + normal(random) * 0.85)))
        : Math.floor(random() * ageOptions.length);
    const row = {
      ID: `SYN-${String(index + 1).padStart(3, "0")}`,
      Age: ageOptions[ageIndex],
      Programme: programmeOptions[Math.floor(random() * programmeOptions.length)],
    };
    scaleValues.forEach((value, itemIndex) => {
      row[`Scale_${itemIndex + 1}`] = value;
    });
    return row;
  });
}

function renderBars(matrix) {
  const counts = [0, 0, 0, 0, 0];
  matrix.flat().forEach((value) => {
    counts[value - 1] += 1;
  });
  const max = Math.max(...counts, 1);
  document.querySelector("#bars").innerHTML = counts
    .map(
      (count, index) => `
        <div class="bar-column">
          <div class="bar-track">
            <div class="bar-fill" data-value="${count}" style="height:${Math.max(3, (count / max) * 100)}%"></div>
          </div>
          <span class="bar-label">${index + 1}</span>
        </div>
      `,
    )
    .join("");
}

function renderPreview(rows) {
  const columns = Object.keys(rows[0] || {});
  document.querySelector("#preview-head").innerHTML = `<tr>${columns
    .map((column) => `<th>${column}</th>`)
    .join("")}</tr>`;
  document.querySelector("#preview-body").innerHTML = rows
    .slice(0, 5)
    .map(
      (row) =>
        `<tr>${columns.map((column) => `<td>${row[column]}</td>`).join("")}</tr>`,
    )
    .join("");
}

function setLanguage(nextLanguage) {
  language = nextLanguage;
  document.documentElement.lang = nextLanguage === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (translations[nextLanguage][key]) {
      element.textContent = translations[nextLanguage][key];
    }
  });
  document.querySelectorAll(".language-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.language === nextLanguage);
  });
}

document.querySelectorAll(".language-button").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.language));
});

document.querySelector("#simulation-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const responseCount = Number(document.querySelector("#responses").value);
  const itemCount = Number(document.querySelector("#items").value);
  const targetMin = Number(document.querySelector("#target-min").value);
  const targetMax = Number(document.querySelector("#target-max").value);
  const seed = Number(document.querySelector("#seed").value);
  const distribution = document.querySelector('input[name="distribution"]:checked').value;

  if (
    !Number.isInteger(responseCount) ||
    responseCount < 20 ||
    responseCount > 1000 ||
    !Number.isInteger(itemCount) ||
    itemCount < 2 ||
    itemCount > 20 ||
    targetMin <= 0 ||
    targetMax >= 1 ||
    targetMin > targetMax
  ) {
    return;
  }

  document.querySelector("#run-state").textContent = translations[language].running;
  const result = calibrate(responseCount, itemCount, seed, targetMin, targetMax);
  if (!result) return;

  currentRows = buildRows(result.matrix, seed, distribution);
  const passed = result.alpha >= targetMin && result.alpha <= targetMax;
  document.querySelector("#alpha-value").textContent = result.alpha.toFixed(3);
  document.querySelector("#sample-value").textContent = String(responseCount);
  document.querySelector("#attempt-value").textContent = String(result.attempt);
  document.querySelector("#distribution-caption").textContent =
    `${responseCount} ${translations[language].rows}`;

  const status = document.querySelector("#result-status");
  status.className = `result-status ${passed ? "is-pass" : "is-warning"}`;
  status.innerHTML = `
    <strong>${passed ? translations[language].passTitle : translations[language].warningTitle}</strong>
    <p>${passed ? translations[language].passBody : translations[language].warningBody}</p>
  `;

  renderBars(result.matrix);
  renderPreview(currentRows);
  document.querySelector("#download").disabled = false;
  document.querySelector("#run-state").textContent = translations[language].complete;
});

document.querySelector("#download").addEventListener("click", () => {
  if (!currentRows.length) return;
  const columns = Object.keys(currentRows[0]);
  const csv = [
    columns.join(","),
    ...currentRows.map((row) => columns.map((column) => row[column]).join(",")),
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "lrobotform-alpha-synthetic.csv";
  link.click();
  URL.revokeObjectURL(link.href);
});

setLanguage("en");
