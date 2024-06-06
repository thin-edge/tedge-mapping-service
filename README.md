# tedge-mapping-service
This is a sample service to map from a custom json format to tedge json format.

Publish custom measurement:
```
tedge mqtt pub custom/signal '{"value":90}'
```

This measurement is converted to:

```
{ "temperature": {"value": 180  } }
```

and published on the topic: `te/device/main///m/c8y_Temperature`