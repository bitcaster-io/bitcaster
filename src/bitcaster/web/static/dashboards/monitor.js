document.addEventListener('alpine:init', () => {
    const INTERVAL = 10 * 1000;
    Alpine.data('celeryHealth', (url) => ({
        url,
        tabWorker: true,
        tabTasks: false,
        alive: false,
        tasksMap: {},
        datetime: null,
        beat: false,
        beatLastUpdate: "",
        flash: false,
        loading: false,
        interval: null,
        error: null,

        runningFrom(timestampMs) {
            if (!timestampMs) return '';

            // Dramatiq Message.timestamp → milliseconds
            const startedMs = Number(timestampMs);
            const nowMs = Date.now();

            let seconds = Math.floor((nowMs - startedMs) / 1000);
            if (seconds < 0) return 'just started';

            const hours = Math.floor(seconds / 3600);
            seconds %= 3600;
            const minutes = Math.floor(seconds / 60);
            seconds %= 60;

            if (hours > 0) return `${hours}h ${minutes}m`;
            if (minutes > 0) return `${minutes}m ${seconds}s`;
            return `${seconds}s`;
        },
        init() {
            this.check()
            this.interval = setInterval(() => this.check(), INTERVAL)
        },

        async check() {
            this.loading = true
            this.flash = true
            this.error = null
            setTimeout(() => this.flash = false, 1000) //  0.5s
            try {
                const res = await fetch(this.url, {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify({})
                })
                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}: ${res.statusText}`)
                }
                const data = await res.json()
                this.beat = Boolean(data.beat.status);
                if (data.beat.seen !== "") {
                    this.beatLastUpdate = new Date(data.beat.seen).toLocaleString(undefined, {
                        dateStyle: "short",
                        timeStyle: "medium"
                    });
                }
                this.datetime = data.datetime || "";
                this.tasksMap = data.workers || {};
                this.alive = Boolean(data.alive) || Object.keys(this.tasksMap).length > 0;
            } catch (e) {
                this.beat = false;
                this.alive = false;
                this.tasksMap = {};
                if (e instanceof TypeError && e.message === "Failed to fetch") {
                    this.error = "Connection refused or network error";
                } else {
                    this.error = e.message;
                }
                console.error("Monitor check failed:", e);
            } finally {
                this.loading = false
            }
        },

        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value
        },

        destroy() {
            if (this.interval) clearInterval(this.interval)
        }
    }))
})
