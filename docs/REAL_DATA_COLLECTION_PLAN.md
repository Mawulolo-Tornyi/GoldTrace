# Real Data Collection Plan

Collect synchronized recordings from both monitoring nodes under normal river flow, rain, heavy rain, runoff/flood turbidity, wind, people/animals, motorcycles/cars/trucks/boats, generators, pumps, construction equipment, excavators and other heavy machinery.

For every event record: event/session ID, node ID, UTC timestamp, location ID, node coordinates, river/segment, weather, machine type/state, approximate machine-to-sensor distance, turbidity, temperature, raw or securely processed audio features, geophone waveform/features, battery/link state, and a verification label with method/notes.

Keep windows from the same event/session together during train/validation/test splits. When enough data exists, reserve whole locations as unseen test locations. Collect both confusing negative examples (e.g. muddy rainwater plus nearby vehicles) and true multi-sensor mining-like disturbances.

Audio collection should minimize privacy impact: prefer environmental/machinery recordings and edge-extracted features; retain raw audio only where authorized and necessary for model development.
