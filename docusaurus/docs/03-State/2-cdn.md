---
sidebar_position: 2
---

# AWS CloudFront

### Overview

CloudFront is used to make files available via Content Delivery Network. 
CDN reduces latency and decreases load on main application. 
Main application returns only one HTML file to each request, which has links to all relevant CDN resources. 
That way webapp can run on smaller nodes.

### Web Application Firewall

AWS offers option to create firewall in front of CDN resources.
For PoC there is a rule that checks if CDN request comes from karlaru.com . 
It only accept requests with header key **referer** valued **https://karlaru.com/**.

:::danger Warning

It is not particularly secure, because one could manually add or change header values in requests. 

:::

:::tip Postman

A good tool to test requests with different header values is [Postman](https://www.postman.com/).

:::
```yaml title="web-acl.yaml"
AWSTemplateFormatVersion: 2010-09-09
Description: CDN Firewall
Resources:
  ACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      DefaultAction:
        Block: {}
      Name: CDN-Firewall
      Scope: CLOUDFRONT
      VisibilityConfig:
        SampledRequestsEnabled: false
        CloudWatchMetricsEnabled: true
        MetricName: ACL
      Rules:
        - Name: 'referer'
          Priority: 0
          Action:
            Allow: {}
          VisibilityConfig:
            SampledRequestsEnabled: false
            CloudWatchMetricsEnabled: true
            MetricName: referer
          Statement:
            ByteMatchStatement:
              SearchString: 'https://karlaru.com/'
              FieldToMatch:
                SingleHeader:
                  Name: 'referer'
              TextTransformations:
                - Priority: 0
                  Type: 'NONE'
              PositionalConstraint: 'EXACTLY'

  ACLAssociation:
    Type: AWS::WAFv2::WebACLAssociation
    Properties:
      ResourceArn: !Ref CloudFront
      WebACLArn: !Ref ACL

```

### CloudFront CloudFormation template

**OPTIONS** method should be allowed, because it enables varius headers.
Otherwise, config snippet should be self-explanatory.

```yaml title="base_stack.yaml"
  CloudFront:
    Type: AWS::CloudFront::Distribution
    DeletionPolicy: Retain
    Properties:
      DistributionConfig:
        Enabled: true
        Origins:
          - DomainName: karlaru-mb.s3.eu-north-1.amazonaws.com
            Id: S3-bucket
            S3OriginConfig:
              OriginAccessIdentity: !Sub 'origin-access-identity/cloudfront/${CloudFrontOriginIdentity}'
        DefaultCacheBehavior:
          AllowedMethods:
            - GET
            - HEAD
            - OPTIONS
          CachedMethods:
            - GET
            - HEAD
            - OPTIONS
          Compress: true
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6
          OriginRequestPolicyId: 88a5eaf4-2fd4-4709-b370-b4c650ea3fcf
          TargetOriginId: S3-bucket
          ViewerProtocolPolicy: https-only
        HttpVersion: http2
        PriceClass: PriceClass_100
        ViewerCertificate:
          CloudFrontDefaultCertificate: true

  CloudFrontOriginIdentity:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: 'comment'

```
