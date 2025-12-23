#!/bin/bash
docker stop reranker-server
docker rm reranker-server
docker run --name reranker-server -p 50051:50051 reranker-server:latest
