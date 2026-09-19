===== config.json =====
{
  "inbounds": [{
    "port": 8080,
    "protocol": "vless",
    "settings": {
      "clients": [{ "id": "f4158cfb-ce02-46aa-8a48-a446c5073c4b" }],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "ws",
      "wsSettings": { "path": "/reo" }
    }
  }],
  "outbounds": [{ "protocol": "freedom" }]
}

===== Dockerfile =====
FROM teddysun/xray:latest
COPY config.json /etc/xray/config.json
CMD sh -c "sed -i s/8080/$PORT/g /etc/xray/config.json && xray -c /etc/xray/config.json"
