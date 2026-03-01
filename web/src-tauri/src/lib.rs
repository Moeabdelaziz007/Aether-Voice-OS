use tauri::Manager;
use tauri_plugin_global_shortcut::{Code, Modifiers, Shortcut, ShortcutState};

#[tauri::command]
async fn check_engine_status() -> Result<String, String> {
    // Ping the local Python Admin API
    let client = reqwest::Client::new();
    match client.get("http://localhost:18790/health").send().await {
        Ok(_) => Ok("online".to_string()),
        Err(_) => Err("offline".to_string()),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .invoke_handler(tauri::generate_handler![check_engine_status])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            // Configure Window for Aether Premium Experience
            if let Some(window) = app.get_webview_window("main") {
                // Pin to top for the Floating HUD experience
                window.set_always_on_top(true)?;
                
                // Mac-specific: allow window to be seen on all spaces/desktops
                #[cfg(target_os = "macos")]
                {
                    use tauri::Runtime;
                    // Note: In Tauri 2.0, some NSWindow methods might require raw handles
                    // but set_always_on_top usually suffices for the initial POC.
                }
            }

            // Register Mac hotkey: Cmd+Option+Space
            let ctrl_alt_space =
                Shortcut::new(Some(Modifiers::SUPER | Modifiers::ALT), Code::Space);
            app.handle().plugin(
                tauri_plugin_global_shortcut::Builder::new()
                    .with_handler(move |app_handle, shortcut, event| {
                        if shortcut == &ctrl_alt_space {
                            if event.state() == ShortcutState::Pressed {
                                if let Some(window) = app_handle.get_webview_window("main") {
                                    if window.is_visible().unwrap_or(false) {
                                        let _ = window.hide();
                                    } else {
                                        let _ = window.show();
                                        let _ = window.set_focus();
                                    }
                                }
                            }
                        }
                    })
                    .build(),
            )?;

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
