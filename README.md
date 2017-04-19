A toy implementation to perform image processing via Lambda and AWS Step Functions.

== Payload ==
This is an example payload sent to Step Function to trigger the lambda event processing:
```json
{ 
  "comment":"an example test run", 
  "source_bucket": "dm-dev-test", 
  "source_key": "source/imagesizetest.jpeg", 
  "dest_bucket": "dm-dev-test", 
  "dest_key": "thumbnails/200x200imagetest.png", 
  "height": "200", 
  "width": "200", 
  "mode": "", 
  "format": "png" }
```

One of the key challenges to designing a lambda function is to encapsulate as much state into the input data as we can so that Lambda doesn't need to rely on other resources directly.  This is similar to message broker architectures that augment and enhance the data on messages prior to processing by some key function.
