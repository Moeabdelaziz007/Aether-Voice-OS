
import { BackpressureController } from "./controllers";

export class PCMStreamBatcher {
    private b: Uint8Array[] = []; 
    private timer: any = null; 
    
    constructor(private ws: WebSocket, private bp: BackpressureController) { }
    
    add(p: Uint8Array) { 
        this.b.push(p); 
        if (!this.timer) this.timer = setTimeout(() => this.flush(), 40); 
    }
    
    private flush() {
        this.timer = null; 
        if (this.ws.readyState !== 1 || this.bp.isThrottled(this.ws.bufferedAmount)) { 
            this.b = []; 
            return; 
        }
        const merged = new Uint8Array(this.b.reduce((a, v) => a + v.length, 0)); 
        let o = 0;
        for (const c of this.b) { 
            merged.set(c, o); 
            o += c.length; 
        }
        this.ws.send(merged); 
        this.b = [];
        this.bp.send(); // Track unacked chunk
    }
}
