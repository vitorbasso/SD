"""The Python implementation of the GRPC standard.Greeter client."""

from __future__ import print_function

import grpc

import standard_pb2
import standard_pb2_grpc


def run():
    channel = grpc.insecure_channel('127.0.1.1:23456')
    stub = standard_pb2_grpc.StandardStub(channel)
    response = stub.Create(standard_pb2.StandardRequest(key=1, value=1))
    response = stub.Read(standard_pb2.StandardRequest(key=1, value=1))
    response = stub.Update(standard_pb2.StandardRequest(key=1, value=1))
    response = stub.Delete(standard_pb2.StandardRequest(key=1, value=1))
    print("Standard client received: " + response.message)


if __name__ == '__main__':
    run()
