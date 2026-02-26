use std::process::Command;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            // Launch the Python backend sidecar
            let sidecar_path = app
                .path()
                .resource_dir()
                .expect("failed to resolve resource dir")
                .join("sidecars")
                .join(if cfg!(windows) {
                    "dravis-bridge.exe"
                } else {
                    "dravis-bridge"
                });

            if sidecar_path.exists() {
                log::info!("Starting DRAVIS backend sidecar: {:?}", sidecar_path);
                let _child = Command::new(&sidecar_path)
                    .spawn()
                    .expect("Failed to start DRAVIS backend sidecar");
            } else {
                log::warn!(
                    "Sidecar not found at {:?}. Running in dev mode (start backend manually).",
                    sidecar_path
                );
            }

            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
