---
slug: /
---

# Overview

## Intro

High level overview of used components.

## State

State of the web application is stored in S3 bucket and two DynamoDB tables. 

<img src="/img/State.svg" width="600"/>

## Triggered functions

Lambda functions that are triggered by:
- uploading new image to **S3** using [Post new image](https://karlaru.com/post) page
- deleting message from **DynamoDB** triggers deletion of all related images (original full sized image, thumbnail etc)

<img src="/img/Triggered.svg" width="600"/>

## Content Delivery Network

All images, scripts and style files are served using content delivery network. 

<img src="/img/CDN.svg" width="600"/>
