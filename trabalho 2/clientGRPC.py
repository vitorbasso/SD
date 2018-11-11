"""The Python implementation of the GRPC standard.Greeter client."""

from __future__ import print_function

import grpc

import standard_pb2
import standard_pb2_grpc


def run():
    channel = grpc.insecure_channel('127.0.1.1:23456')
    stub = standard_pb2_grpc.StandardStub(channel)
    response = stub.Create(
        standard_pb2.StandardRequest(key=123, value='INICIAL'))
    print("Standard client Create received: " + response.message)
    response = stub.Restart(standard_pb2.ResetRequest(
        public_key='c144efbb-c793-4d57-b6ed-7ee40321656e'))
    print("Standard client Create received: " + response.message)
    response = stub.Restart(standard_pb2.ResetRequest(
        public_key='c144efbb-c793-4d57-b66d-7ee40321656e'))
    print("Standard client Create received: " + response.message)
    # response = stub.Read(standard_pb2.StandardRequest(key=2))
    # print("Standard client Read received: " + response.message)
    # response = stub.Update(
    #     standard_pb2.StandardRequest(key=1, value='IUPDATE'))
    # print("Standard client Update received: " + response.message)
    # response = stub.Delete(standard_pb2.StandardRequest(key=3))
    # print("Standard client Delete received: " + response.message)


if __name__ == '__main__':
    run()
