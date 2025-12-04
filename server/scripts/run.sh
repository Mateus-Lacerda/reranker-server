#!/bin/bash
docker stop reranker-server
docker rm reranker-server
docker run --name reranker-server reranker-server:latest
