/**
 * Gemini Live WebSocket — Real Integration Tests.
 *
 * These tests connect to the REAL Gemini Bidi WebSocket API.
 * They verify:
 *   - WebSocket connection + setup handshake
 *   - Audio message format (realtimeInput.mediaChunks)
 *   - Vision frame message format (image/jpeg)
 *   - Tool declarations in setup
 *   - Connection teardown
 *
 * Requires: NEXT_PUBLIC_GEMINI_KEY environment variable.
 */

import { describe, it, expect, beforeAll } from 'vitest';

const GEMINI_WS_URL =
    'wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent';

const API_KEY = process.env.NEXT_PUBLIC_GEMINI_KEY || '';
const MODEL = 'models/gemini-2.5-flash-preview-native-audio-dialog';

// Skip tests entirely if no API key
const describeWithKey = API_KEY ? describe : describe.skip;

describeWithKey('Gemini Live WebSocket — Real Integration', () => {
    beforeAll(() => {
        if (!API_KEY) {
            console.warn('⚠ NEXT_PUBLIC_GEMINI_KEY not set, skipping integration tests');
        }
    });

    it('should connect and receive setupComplete within 10s', async () => {
        const ws = new WebSocket(`${GEMINI_WS_URL}?key=${API_KEY}`);

        const result = await new Promise<{ success: boolean; msg?: string }>((resolve) => {
            const timeout = setTimeout(() => {
                ws.close();
                resolve({ success: false, msg: 'Timeout waiting for setupComplete' });
            }, 10000);

            ws.onopen = () => {
                const setup = {
                    setup: {
                        model: MODEL,
                        generation_config: {
                            response_modalities: ['AUDIO'],
                            speech_config: {
                                voice_config: {
                                    prebuilt_voice_config: { voice_name: 'Aoede' },
                                },
                            },
                        },
                        system_instruction: {
                            parts: [{ text: 'You are Aether. Respond briefly.' }],
                        },
                        tools: [
                            {
                                function_declarations: [
                                    {
                                        name: 'show_silent_hint',
                                        description: 'Display a hint on screen',
                                        parameters: {
                                            type: 'OBJECT',
                                            properties: {
                                                text: { type: 'STRING', description: 'Hint text' },
                                            },
                                            required: ['text'],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                };
                ws.send(JSON.stringify(setup));
            };

            ws.onmessage = (event) => {
                if (typeof event.data === 'string') {
                    const msg = JSON.parse(event.data);
                    if (msg.setupComplete) {
                        clearTimeout(timeout);
                        ws.close();
                        resolve({ success: true });
                    }
                }
            };

            ws.onerror = () => {
                clearTimeout(timeout);
                ws.close();
                resolve({ success: false, msg: 'WebSocket error' });
            };
        });

        expect(result.success).toBe(true);
    }, 15000);

    it('should accept audio PCM chunks without error', async () => {
        const ws = new WebSocket(`${GEMINI_WS_URL}?key=${API_KEY}`);

        const result = await new Promise<{ success: boolean; msg?: string }>((resolve) => {
            const timeout = setTimeout(() => {
                ws.close();
                resolve({ success: false, msg: 'Timeout' });
            }, 15000);

            let setupDone = false;

            ws.onopen = () => {
                const setup = {
                    setup: {
                        model: MODEL,
                        generation_config: {
                            response_modalities: ['AUDIO'],
                            speech_config: {
                                voice_config: {
                                    prebuilt_voice_config: { voice_name: 'Aoede' },
                                },
                            },
                        },
                        system_instruction: {
                            parts: [{ text: 'You are Aether.' }],
                        },
                    },
                };
                ws.send(JSON.stringify(setup));
            };

            ws.onmessage = (event) => {
                if (typeof event.data === 'string') {
                    const msg = JSON.parse(event.data);

                    if (msg.setupComplete) {
                        setupDone = true;

                        // Send a small PCM chunk (256 samples of silence)
                        const pcm = new Int16Array(256).fill(0);
                        const bytes = new Uint8Array(pcm.buffer);
                        let b64 = '';
                        for (let i = 0; i < bytes.length; i += 8192) {
                            b64 += String.fromCharCode(...bytes.subarray(i, i + 8192));
                        }
                        b64 = btoa(b64);

                        const audioMsg = {
                            realtimeInput: {
                                mediaChunks: [
                                    {
                                        mimeType: 'audio/pcm;rate=16000',
                                        data: b64,
                                    },
                                ],
                            },
                        };

                        ws.send(JSON.stringify(audioMsg));

                        // If no error after 3s, it was accepted
                        setTimeout(() => {
                            clearTimeout(timeout);
                            ws.close();
                            resolve({ success: true });
                        }, 3000);
                    }
                }
            };

            ws.onerror = () => {
                clearTimeout(timeout);
                ws.close();
                resolve({ success: false, msg: setupDone ? 'Error after audio send' : 'Connection error' });
            };
        });

        expect(result.success).toBe(true);
    }, 20000);

    it('should accept vision JPEG frames without error', async () => {
        const ws = new WebSocket(`${GEMINI_WS_URL}?key=${API_KEY}`);

        const result = await new Promise<{ success: boolean; msg?: string }>((resolve) => {
            const timeout = setTimeout(() => {
                ws.close();
                resolve({ success: false, msg: 'Timeout' });
            }, 15000);

            ws.onopen = () => {
                const setup = {
                    setup: {
                        model: MODEL,
                        generation_config: {
                            response_modalities: ['AUDIO'],
                            speech_config: {
                                voice_config: {
                                    prebuilt_voice_config: { voice_name: 'Aoede' },
                                },
                            },
                        },
                        system_instruction: {
                            parts: [{ text: 'You are Aether with vision.' }],
                        },
                    },
                };
                ws.send(JSON.stringify(setup));
            };

            ws.onmessage = (event) => {
                if (typeof event.data === 'string') {
                    const msg = JSON.parse(event.data);

                    if (msg.setupComplete) {
                        // Send a tiny valid JPEG (1x1 pixel black)
                        // This is the smallest valid JPEG file
                        const tinyJpegB64 =
                            '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof' +
                            'Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwh' +
                            'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAAR' +
                            'CAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAA' +
                            'AgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkK' +
                            'FhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWG' +
                            'h4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl' +
                            '5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREA' +
                            'AgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYk' +
                            'NOEl8RcYI4Q/RFhScJAiEyUxUGZoY2R0cnODk5OktMTE5QUlNVVzhJWltcX1ZnZ2VodHV2h3' +
                            'eJl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX' +
                            '2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+gD/2Q==';

                        const visionMsg = {
                            realtimeInput: {
                                mediaChunks: [
                                    {
                                        mimeType: 'image/jpeg',
                                        data: tinyJpegB64,
                                    },
                                ],
                            },
                        };

                        ws.send(JSON.stringify(visionMsg));

                        // If no error after 3s, frame was accepted
                        setTimeout(() => {
                            clearTimeout(timeout);
                            ws.close();
                            resolve({ success: true });
                        }, 3000);
                    }
                }
            };

            ws.onerror = () => {
                clearTimeout(timeout);
                ws.close();
                resolve({ success: false, msg: 'WebSocket error' });
            };
        });

        expect(result.success).toBe(true);
    }, 20000);
});
