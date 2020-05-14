# Overview
AWS Tools are a quick throw away set of utilities to manipulate AWS resource.

## PushASGTags
Push tags from ASG's down thru existing instances, more specifically downwards into mounted EBS volumes.  In a more elegant world I'd have probably
used CloudWatch events with Lambdas to detect the volume mounting events to drive tags onto volumes.

## UpdateNames
Quick tool to restore kubernetes PV names on EBS volumes from accidentally over applying PushASGTags :)