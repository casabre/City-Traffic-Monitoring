use std::{
    collections::HashMap,
    env,
    time::{SystemTime, UNIX_EPOCH},
};

pub fn get_sensor_id() -> String {
    let id = env::var("SENSOR_ID").unwrap_or_else(|_| format!("dummy-{}", 1).to_string());
    id
}

pub fn get_mqtt_url() -> String {
    let url = env::var("MQTT_URL").unwrap_or_else(|_| "tcp://mqtt.sctmp.ai:1883".to_string());
    url
}

pub fn get_mqtt_username() -> String {
    let url = env::var("MQTT_USERNAME").unwrap_or_else(|_| "".to_string());
    url
}

pub fn get_mqtt_password() -> String {
    let url = env::var("MQTT_PASSWORD").unwrap_or_else(|_| "".to_string());
    url
}

pub fn get_topics() -> HashMap<String, String> {
    let mut topics = HashMap::new();
    topics.insert("out".to_string(), "sensor/data".to_string());
    topics
}

pub fn get_sample_rate() -> i32 {
    let default = 2_i32.pow(14);
    let sr = env::var("SAMPLE_RATE").unwrap_or_else(|_| format!("{default}").to_string());
    sr.parse::<i32>().unwrap()
}

pub fn get_timestamp() -> u64 {
    match SystemTime::now().duration_since(UNIX_EPOCH) {
        Ok(n) => return n.as_secs(),
        Err(_) => panic!("SystemTime before UNIX EPOCH!"),
    }
}
