use crate::runner::MutableRunner;
use base64::{engine::general_purpose, Engine as _};
use flate2::write::ZlibEncoder;
use flate2::Compression;
use ndarray::{Array2, ShapeBuilder};
use serde_cbor::to_vec;
use serde_derive::Serialize;
use std::collections::HashMap;
use std::env;
use std::io::Write;
#[path = "./utility.rs"]
mod utility;

pub trait Capturing<'a> {
    fn new<'b: 'a, Processor>(sound_forwarder: Processor, sample_rate: i32) -> Self
    where
        Processor: 'b + Fn(Box<dyn erased_serde::Serialize>);
}

#[derive(Serialize)]
struct AudioRaw {
    pub r: Array2<i16>,
    pub rt: String,
    pub ml: String,
    pub cc: usize,
    pub sc: usize,
    pub sr: i32,
}

pub struct Audio<'a> {
    ctx: soundio::Context<'a>,
    input_stream: soundio::InStream<'a>,
}

impl<'a> MutableRunner<'a> for Audio<'a> {
    fn start(&mut self) {
        match self.input_stream.start() {
            Err(e) => panic!("Error starting stream: {}", e),
            Ok(f) => f,
        };
    }
    fn stop(&mut self) {}
}

impl<'a> Capturing<'a> for Audio<'a> {
    fn new<'b: 'a, Processor>(sound_forwarder: Processor, sample_rate: i32) -> Audio<'a>
    where
        Processor: 'b + Fn(Box<dyn erased_serde::Serialize>),
    {
        // Data preparation closure
        let read_callback = move |stream: &mut soundio::InStreamReader| {
            let frame_count_max = stream.frame_count_max();
            if let Err(e) = stream.begin_read(frame_count_max) {
                println!("Error reading from stream: {}", e);
                return;
            }
            let ar = copy_data_and_create_audio_raw_struct(stream, sample_rate);
            let base64_encoded = convert_audio_raw_struct_to_base64_string(ar);
            let sen_ml = create_sen_ml_map(base64_encoded);
            let boxed_sen_ml = Box::new(sen_ml);
            sound_forwarder(boxed_sen_ml);
        };

        // Initialize soundio
        let ctx = create_ctx().unwrap();
        let input_stream: soundio::InStream;
        {
            let dev = create_dev(&ctx, sample_rate).unwrap();
            input_stream = match dev.open_instream(
                sample_rate,
                soundio::Format::S16LE,
                soundio::ChannelLayout::get_builtin(soundio::ChannelLayoutId::Stereo),
                1.0,
                read_callback,
                None::<fn()>,
                None::<fn(soundio::Error)>,
            ) {
                Err(e) => panic!("Error creating stream: {}", e),
                Ok(f) => f,
            };
        }

        Audio {
            ctx: ctx,
            input_stream: input_stream,
        }
    }
}

/// Create a SenML map out of the retrieved sound data
fn create_sen_ml_map(base64_encoded: String) -> HashMap<String, String> {
    let mut sen_ml = HashMap::new();
    let name = format!("{}_audio", utility::get_sensor_id());
    let timestamp = format!("{}", utility::get_timestamp());
    sen_ml.insert("n".to_string(), name.to_string());
    sen_ml.insert("t".to_string(), timestamp.to_string());
    sen_ml.insert("vd".to_string(), base64_encoded.to_string());
    sen_ml.insert("ct".to_string(), "application/gzip".to_string());
    sen_ml
}

/// gzip the AudioRaw data and encode it to a base64 string
fn convert_audio_raw_struct_to_base64_string(ar: AudioRaw) -> String {
    let data = to_vec(&ar).unwrap();
    let mut zip_engine = ZlibEncoder::new(Vec::new(), Compression::default());
    if let Err(e) = zip_engine.write_all(&data) {
        println!("Error reading from stream: {}", e);
    };
    let compressed_bytes = zip_engine.finish().unwrap();
    let base64_encoded = general_purpose::URL_SAFE_NO_PAD.encode(&compressed_bytes);
    base64_encoded
}

/// Copy the data from the audio stream into a vector per stream and a separate
/// index in a hashmap and return a AudioRaw struct
/// TODO: use ndarray in the release version instead of the hashmap
fn copy_data_and_create_audio_raw_struct(
    stream: &mut soundio::InStreamReader,
    sample_rate: i32,
) -> AudioRaw {
    let frames = stream.frame_count();
    let channels = stream.channel_count();
    let getter = |cc, ff| {
        let data = stream.sample::<i16>(cc, ff);
        data
    };
    let dim = ndarray::Dim([frames, channels]);
    let mut arr = Array2::zeros(dim.f());
    for f in 0..frames {
        for c in 0..channels {
            arr[[f, c]] = getter(c, f);
        }
    }
    let ar = AudioRaw {
        r: arr,
        rt: "S16LE".to_string(),
        ml: "column".to_string(),
        cc: channels,
        sc: frames,
        sr: sample_rate,
    };
    ar
}

/// Create a soundio context
fn create_ctx<'a>() -> Result<soundio::Context<'a>, soundio::Error> {
    let mut ctx = soundio::Context::new();
    ctx.set_app_name("Recorder");
    match ctx.connect() {
        Err(e) => panic!("Error connecting soundio context: {}", e),
        Ok(f) => f,
    };
    ctx.flush_events();
    Ok(ctx)
}

/// Create a soundio device
fn create_dev<'a>(
    ctx: &'a soundio::Context,
    sample_rate: i32,
) -> Result<soundio::Device<'a>, soundio::Error> {
    let device_name = env::var("INPUT_DEVICE").unwrap_or("".to_string());
    let mut dev: Option<soundio::Device> = None;
    if !device_name.is_empty() {
        let devices = ctx.input_devices().unwrap();
        for device in devices {
            let name = device.name().to_lowercase();
            dev = match name {
                device_name => Some(device),
                _ => None,
            };
        }
    }
    if let None = dev {
        dev = Some(ctx.default_input_device().expect("No input device"));
        println!("Using default input device")
    }
    if !dev
        .as_ref()
        .unwrap()
        .supports_layout(soundio::ChannelLayout::get_builtin(
            soundio::ChannelLayoutId::Stereo,
        ))
    {
        panic!("Device doesn't support stereo");
    }
    if !dev
        .as_ref()
        .unwrap()
        .supports_format(soundio::Format::S16LE)
    {
        panic!("Device doesn't support S16LE");
    }
    if !dev.as_ref().unwrap().supports_sample_rate(sample_rate) {
        let khz: f32 = sample_rate as f32 / 1000.0;
        panic!("Device doesn't support {khz} kHz");
    }
    Ok(dev.unwrap())
}
