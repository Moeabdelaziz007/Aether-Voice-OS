
import nacl from "tweetnacl";

export class HandshakeManager {
    private kp: nacl.SignKeyPair | null = null;

    constructor() {
        // Enforce ephemeral keys: generate a fresh keypair on every connection
        const seed = nacl.randomBytes(32);
        this.kp = nacl.sign.keyPair.fromSeed(seed);

        // Zeroize the seed buffer immediately after usage
        seed.fill(0);
    }

    generateResponse(ch: string) {
        if (!this.kp) throw new Error("Keypair already zeroized");
        const sig = nacl.sign.detached(this.fh(ch), this.kp.secretKey);
        return { client_id: this.th(this.kp.publicKey), signature: this.th(sig) };
    }

    signIntent(i: string) {
        if (!this.kp) throw new Error("Keypair already zeroized");
        return this.th(nacl.sign.detached(new TextEncoder().encode(i), this.kp.secretKey));
    }

    zeroize() {
        // Secure wipe of private key material
        if (this.kp) {
            const sk = this.kp.secretKey as Uint8Array;
            sk.fill(0);
            this.kp = null;
        }
    }

    private th(d: Uint8Array) { return Array.from(d).map(b => b.toString(16).padStart(2, '0')).join(''); }
    private fh(h: string) { const b = new Uint8Array(h.length / 2); for (let i = 0; i < h.length; i += 2) b[i / 2] = parseInt(h.slice(i, i + 2), 16); return b; }
}
