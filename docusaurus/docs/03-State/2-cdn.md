---
sidebar_position: 2
---

# CloudFront

CloudFormation template snippet

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
