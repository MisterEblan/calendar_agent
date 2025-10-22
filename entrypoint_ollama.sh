#!/bin/bash

/bin/ollama serve &
sleep 5
ollama pull gpt-oss:20b-cloud

wait
