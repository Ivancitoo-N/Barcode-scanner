const modalCode = document.getElementById('modal-code-display');
const modalProductInput = document.getElementById('modal-product-input');
const modalType = document.getElementById('modal-type-display');
const btnAdd = document.getElementById('btn-add');
const btnIgnore = document.getElementById('btn-ignore');
const btnFlashlight = document.getElementById('btn-flashlight');
const totalCount = document.getElementById('total-count');
const statsToday = document.getElementById('stats-today');
const codeList = document.getElementById('code-list');
const modal = document.getElementById('confirm-modal');
const searchInput = document.getElementById('search-input');
const sortSelect = document.getElementById('sort-select');

// --- Audio Feedback System ---
class ScannerAudio {
    constructor() {
        this.ctx = null;
    }

    init() {
        if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }

    beep() {
        if (!this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'square';
        osc.frequency.setValueAtTime(880, this.ctx.currentTime); // A5 note
        osc.frequency.exponentialRampToValueAtTime(1760, this.ctx.currentTime + 0.05);

        gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.1);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.1);
    }
}

const audio = new ScannerAudio();
let userInteracted = false;

document.addEventListener('click', () => {
    if (!userInteracted) {
        audio.init();
        userInteracted = true;
    }
}, { once: true });

let isModalOpen = false;
let pendingCode = null;
let scannedCodes = new Set();
let allCodes = []; // Local cache for filtering/sorting
let trendsChart = null;

// --- Analytics Chart ---
function initChart() {
    const ctx = document.getElementById('trendsChart').getContext('2d');
    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Scans',
                data: [],
                borderColor: '#00f2ff',
                backgroundColor: 'rgba(0, 242, 255, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#8e8e93', stepSize: 1, font: { size: 9 } },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                }
            }
        }
    });
}

async function updateChart() {
    try {
        const res = await fetch('/api/stats/hourly');
        const stats = await res.json();
        trendsChart.data.labels = stats.labels;
        trendsChart.data.datasets[0].data = stats.data;
        trendsChart.update();
    } catch (e) { console.error("Stats fetch failed", e); }
}

// Flashlight Toggle
btnFlashlight.addEventListener('click', () => {
    document.body.classList.toggle('flashlight-mode');
    if (document.body.classList.contains('flashlight-mode')) {
        btnFlashlight.innerHTML = '💡';
    } else {
        btnFlashlight.innerHTML = '🔦';
    }
});

// --- Event Listeners ---
const btnClearAll = document.getElementById('btn-clear-all');
btnClearAll.addEventListener('click', async () => {
    if (confirm('Are you sure you want to CLEAR ALL history? This cannot be undone.')) {
        await fetch('/api/codes/all', { method: 'DELETE' });
        allCodes = [];
        scannedCodes.clear();
        filterAndRender();
        updateStats();
        updateChart();
    }
});

// Search & Sort Listeners
searchInput.addEventListener('input', () => filterAndRender());
sortSelect.addEventListener('change', () => filterAndRender());

// Initial Load
initChart();
fetchCodes();
updateChart();

// Polling for new codes
setInterval(async () => {
    if (isModalOpen) return;

    try {
        const response = await fetch('/api/latest_codes');
        const codes = await response.json();

        if (codes && codes.length > 0) {
            const codeObj = codes[0];
            const codeStr = codeObj.data;

            if (!scannedCodes.has(codeStr)) {
                // Determine if we should auto-add or open modal
                const isKnown = codeObj.product_name && codeObj.product_name !== "Product Unknown";

                // Feedback (Beep and Flash)
                audio.beep();
                const ov = document.getElementById('overlay');
                ov.style.background = isKnown ? 'var(--accent)' : 'var(--primary)';
                ov.textContent = isKnown ? `RECOGNIZED (${codeObj.scan_count}x)` : 'NEW CODE';

                setTimeout(() => {
                    ov.style.background = 'rgba(0, 0, 0, 0.6)';
                    ov.textContent = 'Scanning...';
                }, 1000);

                if (isKnown) {
                    await saveCode(codeObj);
                } else {
                    openModal(codeObj);
                }
            }
        }
    } catch (e) {
        console.error("Polling error:", e);
    }
}, 500);

async function saveCode(codeObj) {
    try {
        // If it's a manual add, the name is already in codeObj.product_name from the input
        // If it's an auto-add, it uses the name from the API
        const res = await fetch('/api/codes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(codeObj)
        });
        const savedCode = await res.json();

        allCodes.unshift(savedCode);
        scannedCodes.add(codeObj.data);

        filterAndRender();
        updateStats();
        updateChart();
    } catch (e) {
        console.error("Save failed", e);
    }
}

async function fetchCodes() {
    try {
        const res = await fetch('/api/codes');
        const codes = await res.json();
        allCodes = codes; // Update cache

        scannedCodes.clear();
        codes.forEach(code => scannedCodes.add(code.data));

        filterAndRender();
        updateStats();
    } catch (e) {
        console.error("Failed to fetch codes:", e);
    }
}

function filterAndRender() {
    const searchTerm = searchInput.value.toLowerCase();
    const sortBy = sortSelect.value;

    let filtered = allCodes.filter(c => {
        const name = (c.product_name || "").toLowerCase();
        const data = (c.data || "").toLowerCase();
        return name.includes(searchTerm) || data.includes(searchTerm);
    });

    // Sort
    if (sortBy === 'newest') {
        filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    } else if (sortBy === 'oldest') {
        filtered.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    } else if (sortBy === 'name') {
        filtered.sort((a, b) => (a.product_name || a.data).localeCompare(b.product_name || b.data));
    }

    renderList(filtered);
}

function renderList(codes) {
    codeList.innerHTML = '';
    codes.forEach(c => renderCodeItem(c));
}

function renderCodeItem(codeObj) {
    const li = document.createElement('li');
    li.className = 'code-item';
    li.dataset.id = codeObj.id;

    const timeStr = new Date(codeObj.timestamp).toLocaleString([], {
        day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
    });

    // Count occurrences in local cache
    const count = allCodes.filter(c => c.data === codeObj.data).length;

    li.innerHTML = `
            <div style="flex-grow: 1; min-width: 0;">
                <div class="code-text" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    ${codeObj.product_name ? codeObj.product_name : codeObj.data}
                </div>
                <span class="code-meta">
                    ${codeObj.type} • ${codeObj.data} • ${timeStr}
                    ${count > 1 ? `<span style="color:var(--accent)">[${count}x]</span>` : ''}
                </span>
            </div>
            <button class="btn btn-secondary delete-btn" style="padding: 4px 8px; font-size: 0.8em; margin-left: 10px;" onclick="deleteCode(${codeObj.id})">🗑</button>
        `;

    codeList.appendChild(li);
}

// Global scope for onclick
window.deleteCode = async (id) => {
    if (!confirm('Delete this code?')) return;
    try {
        await fetch(`/api/codes/${id}`, { method: 'DELETE' });

        // Update local state
        const index = allCodes.findIndex(c => c.id === id);
        if (index !== -1) {
            // Check if it's the last one of its kind before removing from Set
            const dataVal = allCodes[index].data;
            allCodes.splice(index, 1);
            if (!allCodes.some(c => c.data === dataVal)) {
                scannedCodes.delete(dataVal);
            }
        }

        filterAndRender();
        updateStats();
        updateChart();
    } catch (e) {
        console.error("Delete failed", e);
    }
};

function updateStats() {
    totalCount.textContent = allCodes.length;

    const today = new Date().toDateString();
    const countToday = allCodes.filter(c => new Date(c.timestamp).toDateString() === today).length;
    statsToday.textContent = `Today: ${countToday}`;
}

function openModal(codeObj) {
    isModalOpen = true;
    pendingCode = codeObj;
    modalCode.textContent = codeObj.data;
    modalProductInput.value = (codeObj.product_name && codeObj.product_name !== "Product Unknown") ? codeObj.product_name : "";

    // Add count to modal
    modalType.innerHTML = `${codeObj.type} ${codeObj.scan_count > 1 ? `<br><span style="color:var(--accent)">Scanned ${codeObj.scan_count} times before</span>` : ''}`;

    modal.classList.remove('hidden');

    setTimeout(() => modalProductInput.focus(), 100);
}

function closeModal() {
    isModalOpen = false;
    pendingCode = null;
    modal.classList.add('hidden');
}

btnAdd.addEventListener('click', async () => {
    if (pendingCode) {
        pendingCode.product_name = modalProductInput.value || "Custom Product";
        await saveCode(pendingCode);
        closeModal();
        setTimeout(() => { isModalOpen = false; }, 1000);
    }
});

btnIgnore.addEventListener('click', () => {
    closeModal();
    setTimeout(() => { isModalOpen = false; }, 1000);
});

modalProductInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        btnAdd.click();
    }
});
