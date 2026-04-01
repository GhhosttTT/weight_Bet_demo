package com.weightloss.betting.ui.main

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Observer
import com.weightloss.betting.R
import com.weightloss.betting.data.model.DietRecommendation
import com.weightloss.betting.data.model.ExerciseRecommendation
import com.weightloss.betting.databinding.FragmentCoachBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class CoachFragment : Fragment() {
    
    private var _binding: FragmentCoachBinding? = null
    private val binding get() = _binding!!
    private val viewModel: CoachViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCoachBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupObservers()
        loadRecommendation()
    }
    
    private fun setupObservers() {
        viewModel.recommendationState.observe(viewLifecycleOwner, Observer { state ->
            when (state) {
                is CoachState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                }
                is CoachState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    
                    val recommendation = state.recommendation
                    
                    binding.tvCalories.text = recommendation.dailyCaloriesTarget?.toString() ?: "--"
                    binding.tvWater.text = recommendation.waterIntakeTarget?.toString() ?: "--"
                    binding.tvSleep.text = recommendation.sleepTarget?.toString() ?: "--"
                    
                    displayExerciseRecommendations(recommendation.exerciseRecommendations)
                    displayDietRecommendations(recommendation.dietRecommendations)
                    
                    if (recommendation.tips != null) {
                        binding.cvTips.visibility = View.VISIBLE
                        binding.tvTips.text = recommendation.tips
                    } else {
                        binding.cvTips.visibility = View.GONE
                    }
                }
                is CoachState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
                is CoachState.Empty -> {
                    binding.progressBar.visibility = View.GONE
                    binding.tvEmptyMessage.visibility = View.VISIBLE
                }
            }
        })
    }
    
    private fun loadRecommendation() {
        viewModel.loadRecommendation()
    }
    
    private fun displayExerciseRecommendations(recommendations: List<ExerciseRecommendation>) {
        binding.llExerciseRecommendations.removeAllViews()
        
        if (recommendations.isEmpty()) {
            val emptyView = TextView(requireContext()).apply {
                text = "暂无运动推荐"
                textSize = 16f
                setTextColor(resources.getColor(R.color.xui_config_color_text_gray))
            }
            binding.llExerciseRecommendations.addView(emptyView)
            return
        }
        
        for (exercise in recommendations) {
            val exerciseView = LayoutInflater.from(requireContext())
                .inflate(R.layout.item_exercise_recommendation, binding.llExerciseRecommendations, false)
            
            exerciseView.findViewById<TextView>(R.id.tvExerciseType).text = exercise.type
            exerciseView.findViewById<TextView>(R.id.tvExerciseDuration).text = "${exercise.duration}分钟"
            exerciseView.findViewById<TextView>(R.id.tvExerciseIntensity).text = getIntensityText(exercise.intensity)
            exerciseView.findViewById<TextView>(R.id.tvExerciseDescription).text = exercise.description ?: ""
            
            binding.llExerciseRecommendations.addView(exerciseView)
        }
    }
    
    private fun displayDietRecommendations(recommendations: List<DietRecommendation>) {
        binding.llDietRecommendations.removeAllViews()
        
        if (recommendations.isEmpty()) {
            val emptyView = TextView(requireContext()).apply {
                text = "暂无饮食推荐"
                textSize = 16f
                setTextColor(resources.getColor(R.color.xui_config_color_text_gray))
            }
            binding.llDietRecommendations.addView(emptyView)
            return
        }
        
        for (diet in recommendations) {
            val dietView = LayoutInflater.from(requireContext())
                .inflate(R.layout.item_diet_recommendation, binding.llDietRecommendations, false)
            
            dietView.findViewById<TextView>(R.id.tvMealType).text = getMealTypeText(diet.mealType)
            dietView.findViewById<TextView>(R.id.tvFoodItems).text = diet.foodItems.joinToString("、")
            dietView.findViewById<TextView>(R.id.tvCalories).text = diet.calories?.let { "${it}千卡" } ?: ""
            dietView.findViewById<TextView>(R.id.tvDietTips).text = diet.tips ?: ""
            
            binding.llDietRecommendations.addView(dietView)
        }
    }
    
    private fun getIntensityText(intensity: String): String {
        return when (intensity.lowercase()) {
            "low" -> "低强度"
            "medium" -> "中强度"
            "high" -> "高强度"
            else -> intensity
        }
    }
    
    private fun getMealTypeText(mealType: String): String {
        return when (mealType.lowercase()) {
            "breakfast" -> "早餐"
            "lunch" -> "午餐"
            "dinner" -> "晚餐"
            "snack" -> "加餐"
            else -> mealType
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
