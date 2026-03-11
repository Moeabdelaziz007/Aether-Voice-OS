
export class BackpressureController {
    HIGH = 65536;
    MAX_UNACKED = 15;
    unacked = 0;

    isThrottled(ba: number) {
        return ba > this.HIGH || this.unacked >= this.MAX_UNACKED;
    }

    send() { this.unacked++; }
    ack() { this.unacked = Math.max(0, this.unacked - 1); }
}

export class ReconnectionManager {
    attempt = 0; timer: any = null; constructor(private onR: () => void) { }
    MAX_ATTEMPTS = 10;
    trigger() {
        this.stop();
        if (this.attempt >= this.MAX_ATTEMPTS) {
            console.error("❌ Aether Gateway: Max reconnection attempts reached.");
            return;
        }
        const delay = Math.min(1000 * Math.pow(1.5, this.attempt++) + Math.random() * 500, 15000);
        console.log(`↻ Aether Gateway Reconnecting in ${Math.round(delay)}ms (Attempt ${this.attempt}/${this.MAX_ATTEMPTS})`);
        this.timer = setTimeout(() => this.onR(), delay);
    }
    stop() { if (this.timer) clearTimeout(this.timer); }
    reset() { this.attempt = 0; this.stop(); }
}
