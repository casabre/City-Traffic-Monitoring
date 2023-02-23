#![crate_name = "sensor_rust"]

mod audio;
mod publishing;
mod runner;
use crate::audio::Capturing;
use crate::publishing::Authentication;
use crate::publishing::Publishing;
use crate::runner::MutableRunner;
use crate::runner::Runner;
use audio::Audio;
use log::info;
use publishing::MqttPublisher;
mod utility;

fn main() {
    info!("Starting capturing and forwarding");
    let id = utility::get_sensor_id();
    let mqtt_url = utility::get_mqtt_url();
    let topics = utility::get_topics();
    let sample_rate = utility::get_sample_rate();
    let mqtt_username = utility::get_mqtt_username();
    let mqtt_password = utility::get_mqtt_password();
    let mqtt = MqttPublisher::new(
        mqtt_url,
        id,
        topics,
        Authentication {
            username: mqtt_username,
            password: mqtt_password,
        },
    );
    let mut audio_sensor = Audio::new(|x| mqtt.append(x), sample_rate);
    audio_sensor.start();
    mqtt.start();
    // should not go here because MqttPublisher loop is blocking
}
