
package com.kingmemo.photostudio

import android.content.Context
import android.graphics.Bitmap
import ai.onnxruntime.*
import java.nio.FloatBuffer

class AiEngine(context: Context) {

    private val env = OrtEnvironment.getEnvironment()
    private val session: OrtSession

    init {
        val model = context.assets.open("u2netp.onnx").use {
            it.readBytes()
        }
        session = env.createSession(model)
    }

    fun removeBackground(bitmap: Bitmap): Bitmap {
        val size = 320
        val inputBitmap = Bitmap.createScaledBitmap(bitmap, size, size, true)

        val input = FloatArray(1 * 3 * size * size)
        val pixels = IntArray(size * size)
        inputBitmap.getPixels(pixels, 0, size, 0, 0, size, size)

        val plane = size * size

        for (i in pixels.indices) {
            val pixel = pixels[i]

            val r = ((pixel shr 16) and 255) / 255f
            val g = ((pixel shr 8) and 255) / 255f
            val b = (pixel and 255) / 255f

            input[i] = (r - 0.485f) / 0.229f
            input[plane + i] = (g - 0.456f) / 0.224f
            input[2 * plane + i] = (b - 0.406f) / 0.225f
        }

        val tensor = OnnxTensor.createTensor(
            env,
            FloatBuffer.wrap(input),
            longArrayOf(1, 3, 320, 320)
        )

        val result = session.run(mapOf("input.1" to tensor))
        val output = result[0].value as Array<Array<Array<FloatArray>>>
        val mask = output[0][0]

        var min = Float.MAX_VALUE
        var max = -Float.MAX_VALUE

        for (row in mask) {
            for (v in row) {
                if (v < min) min = v
                if (v > max) max = v
            }
        }

        val out = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)

        for (y in 0 until size) {
            for (x in 0 until size) {
                val normalized = (mask[y][x] - min) / (max - min + 1e-8f)
                val alpha = (normalized * 255).toInt().coerceIn(0, 255)
                val color = pixels[y * size + x]
                out.setPixel(x, y, (alpha shl 24) or (color and 0x00FFFFFF))
            }
        }

        tensor.close()
        result.close()

        return Bitmap.createScaledBitmap(out, bitmap.width, bitmap.height, true)
    }
}
