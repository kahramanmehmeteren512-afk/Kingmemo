
package com.kingmemo.photostudio

import android.os.Bundle
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.view.Gravity
import android.widget.*
import android.graphics.Color
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import java.util.concurrent.Executors

class MainActivity : ComponentActivity() {

    private lateinit var preview: ImageView
    private lateinit var aiEngine: AiEngine
    private var selectedBitmap: Bitmap? = null
    private val executor = Executors.newSingleThreadExecutor()

    private val picker = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        if (uri != null) {
            try {
                val bitmap = contentResolver.openInputStream(uri)?.use {
                    BitmapFactory.decodeStream(it)
                }

                if (bitmap != null) {
                    selectedBitmap = bitmap
                    preview.setImageBitmap(bitmap)
                }
            } catch (e: Exception) {
                Toast.makeText(this, "Fotoğraf açılamadı", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        aiEngine = AiEngine(this)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(24, 30, 24, 24)
            setBackgroundColor(Color.rgb(22, 22, 30))
        }

        val title = TextView(this).apply {
            text = "KING PHOTO STUDIO"
            textSize = 27f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }

        preview = ImageView(this).apply {
            scaleType = ImageView.ScaleType.FIT_CENTER
            setBackgroundColor(Color.rgb(40, 40, 50))
        }

        val choose = Button(this).apply {
            text = "FOTOĞRAF SEÇ"
            setOnClickListener {
                picker.launch("image/*")
            }
        }

        val remove = Button(this).apply {
            text = "ARKA PLANI SİL"
            setOnClickListener {
                val bitmap = selectedBitmap

                if (bitmap == null) {
                    Toast.makeText(this@MainActivity, "Önce fotoğraf seç", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }

                isEnabled = false
                text = "İŞLENİYOR..."

                executor.execute {
                    try {
                        val result = aiEngine.removeBackground(bitmap)

                        runOnUiThread {
                            selectedBitmap = result
                            preview.setImageBitmap(result)
                            isEnabled = true
                            text = "ARKA PLANI SİL"
                            Toast.makeText(this@MainActivity, "İşlem tamamlandı!", Toast.LENGTH_SHORT).show()
                        }
                    } catch (e: Exception) {
                        runOnUiThread {
                            isEnabled = true
                            text = "ARKA PLANI SİL"
                            Toast.makeText(this@MainActivity, "Hata: ${e.message}", Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
        }

        layout.addView(title)
        layout.addView(preview, LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f
        ))
        layout.addView(choose)
        layout.addView(remove)

        setContentView(layout)
    }

    override fun onDestroy() {
        executor.shutdown()
        super.onDestroy()
    }
}
