#include "cuda/environment_light.hpp"

#include <iostream> // fixme

#include "assert_macros.hpp"
#include "moana/core/coordinates.hpp"
#include "moana/core/vec3.hpp"

namespace moana { namespace EnvironmentLight {

__global__ static void environmentLightKernel(
    int width,
    int height,
    cudaTextureObject_t textureObject,
    float *directionBuffer,
    float *outputBuffer
) {
    const int row = threadIdx.y + blockIdx.y * blockDim.y;
    const int col = threadIdx.x + blockIdx.x * blockDim.x;

    if ((row >= height) || (col >= width)) return;

    const int directionIndex = 3 * (row * width + col);
    Vec3 direction(
        directionBuffer[directionIndex + 0],
        directionBuffer[directionIndex + 1],
        directionBuffer[directionIndex + 2]
    );

    float phi, theta;
    Coordinates::cartesianToSpherical(direction, &phi, &theta);

    // fixme
    phi += 115.f / 180.f * M_PI;
    if (phi > 2.f * M_PI) {
        phi -= 2.f * M_PI;
    }

    float4 environment = tex2D<float4>(
        textureObject,
        phi / (M_PI * 2.f),
        theta / M_PI
    );

    const int outputIndex = 3 * (row * width + col);
    outputBuffer[outputIndex + 0] = environment.x;
    outputBuffer[outputIndex + 1] = environment.y;
    outputBuffer[outputIndex + 2] = environment.z;
}

void calculateEnvironmentLighting(
    int width,
    int height,
    cudaTextureObject_t textureObject,
    float *devDirectionBuffer,
    std::vector<float> &outputBuffer
) {
    const size_t outputBufferSizeInBytes = outputBuffer.size() * sizeof(float);
    CUdeviceptr d_outputBuffer = 0;
    CHECK_CUDA(cudaMalloc(
        reinterpret_cast<void **>(&d_outputBuffer),
        outputBufferSizeInBytes
    ));
    CHECK_CUDA(cudaMemset(
        reinterpret_cast<void *>(d_outputBuffer),
        0,
        outputBufferSizeInBytes
    ));

    const int blockWidth = 16;
    const int blockHeight = 16;

    const dim3 blocks(width / blockWidth + 1, height / blockHeight + 1);
    const dim3 threads(blockWidth, blockHeight);

    environmentLightKernel<<<blocks, threads>>>(
        width,
        height,
        textureObject,
        devDirectionBuffer,
        reinterpret_cast<float *>(d_outputBuffer)
    );

    CHECK_CUDA(cudaMemcpy(
        outputBuffer.data(),
        reinterpret_cast<void *>(d_outputBuffer),
        outputBufferSizeInBytes,
        cudaMemcpyDeviceToHost
    ));

    CHECK_CUDA(cudaFree(reinterpret_cast<void *>(d_outputBuffer)));

    CHECK_CUDA(cudaDeviceSynchronize());
}

} }
