
package com.kingmemo.photostudio

import androidx.activity.ComponentActivity
import android.os.Bundle
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.view.Gravity
import android.widget.*
import android.graphics.Color
import androidx.activity.result.contract.ActivityResultContracts
import java.io.InputStream

class MainActivity : ComponentActivity() {

    private lateinit var preview: ImageView
    private var selectedUri: Uri? = null

    private val picker = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        if (uri != null) {
            selectedUri = uri
            preview.setImageURI(uri)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

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

        layout.addView(title)
        layout.addView(preview, LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f
        ))
        layout.addView(choose)

        setContentView(layout)
    }
}
