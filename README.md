An example Google AppEngine project using Cloud Endpoints and custom authentication.

The supported workflow:
 - A mobile client authenticates via a third-party provider using a native SDK flow, in this case with Facebook.
 - The Facebook access token is sent to the AppEngine app, who verifies and returns its own access token in response, creating a new User entity if necessary.
 - The client includes that token in each endpoints service request using in the `Authorization` header.
 - The endpoints method uses the access token to retrieve the authenticated user.

This is intentionally a narrow use case, but should help inspire ideas on different approaches as well.

## Dependencies
1. [webapp2](http://webapp-improved.appspot.com/index.html) is used for the access token exchange handler
2. [webapp2_extras.appengine](http://webapp-improved.appspot.com/api/webapp2_extras/appengine/auth/models.html) provides a custom User model
3. [simpleauth](https://github.com/crhym3/simpleauth) is included a submodule and is used to verify provider access tokens

## Usage

1. Check out the project and submodules
  ```bash
  git clone git@github.com:loudnate/appengine-endpoints-auth-example.git
  git submodule update
  ```

2. [Generate a client application](https://developers.google.com/appengine/docs/python/endpoints/gen_clients) for your endpoints
3. Include the [Facebook SDK](https://developers.facebook.com/docs/facebook-login) and implement a login flow
4. Exchange the Facebook access token for one provided by your app
  ```bash
  POST /oauth2/access_token HTTP/1.1
  Host: https://your-app-id.appspot.com
  Cache-Control: no-cache
  Content-Type: application/x-www-form-urlencoded

  x_access_token=facebook-access-token&x_provider=facebook
  ```
  ```json
  {
    "token_type": "Bearer",
    "refresh_token": "6oqmYZSaQ72nZfEYlD5PZF",
    "access_token": "nc7Omfm4vgP0swqodJyDeN",
    "expires_in": 31536000
  }
  ```
  ```obj-c
  AFHTTPRequestOperationManager *manager = [AFHTTPRequestOperationManager manager];
  NSDictionary *parameters = @{@"x_access_token": @"facebook-access-token", @"x_provider": @"facebook"};
  
  manager.responseSerializer = [AFJSONResponseSerializer serializer];
  [manager POST:@"https://your-app-id.appspot.com/oauth2/access_token" 
     parameters:parameters 
        success:^(AFHTTPRequestOperation *operation, id responseObject) {
    // ...
  } failure:^(AFHTTPRequestOperation *operation, NSError *error) {
    // ...
  }];
  ```
5. Store the credentials [somewhere appropriate](https://developer.apple.com/library/ios/documentation/security/conceptual/keychainServConcepts/02concepts/concepts.html) and send them with each endpoints service request
  ```obj-c
  GTLServiceHelloworld *service = [[GTLServiceHelloworld alloc] init];
  NSString *authHeaderValue = [NSString stringWithFormat:@"%@ %@", responseObject[@"token_type"], responseObject[@"access_token"]];

  service.additionalHTTPHeaders = @{@"Authorization": authHeaderValue};
  ```
