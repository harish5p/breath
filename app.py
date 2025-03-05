import streamlit as st
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from PIL import Image
import io

def create_breathing_app():
    st.title("Breathing Visualization App")
    
    # Sidebar for controls
    st.sidebar.header("Breathing Settings")
    
    # Breathing rate control
    breaths_per_minute = st.sidebar.slider(
        "Breaths per minute", 
        min_value=1, 
        max_value=30, 
        value=6,
        help="Number of complete breath cycles per minute"
    )
    
    # Calculate total cycle time in seconds
    total_cycle_time = 60 / breaths_per_minute
    
    # Breathing phase distribution
    st.sidebar.subheader("Breath Phase Distribution (%)")
    col1, col2, col3 = st.sidebar.columns(3)
    
    with col1:
        inhale_percent = st.number_input("Inhale", min_value=10, max_value=80, value=40)
    
    with col2:
        exhale_percent = st.number_input("Exhale", min_value=10, max_value=80, value=40)
    
    with col3:
        hold_percent = st.number_input("Hold", min_value=0, max_value=80, value=20)
    
    # Validate percentages sum to 100
    total_percent = inhale_percent + exhale_percent + hold_percent
    if total_percent != 100:
        st.sidebar.warning(f"Percentages sum to {total_percent}%. Please adjust to total 100%.")
        st.sidebar.info("Adjusting proportionally to maintain your distribution...")
        
        # Adjust proportionally
        scale_factor = 100 / total_percent
        inhale_percent = int(inhale_percent * scale_factor)
        exhale_percent = int(exhale_percent * scale_factor)
        hold_percent = 100 - inhale_percent - exhale_percent
        
        st.sidebar.text(f"Adjusted to: Inhale {inhale_percent}%, Exhale {exhale_percent}%, Hold {hold_percent}%")
    
    # Calculate actual times
    inhale_time = (inhale_percent / 100) * total_cycle_time
    exhale_time = (exhale_percent / 100) * total_cycle_time
    hold_time = (hold_percent / 100) * total_cycle_time
    
    # Display timing information
    st.sidebar.subheader("Timing (seconds)")
    st.sidebar.text(f"Inhale: {inhale_time:.1f}s")
    st.sidebar.text(f"Exhale: {exhale_time:.1f}s")
    st.sidebar.text(f"Hold: {hold_time:.1f}s")
    st.sidebar.text(f"Total cycle: {total_cycle_time:.1f}s")
    
    # Visualization style
    viz_style = st.sidebar.selectbox(
        "Visualization Style",
        ["Circle", "Lung", "Wave"],
        index=0
    )
    
    # Start/Stop control
    start_button = st.sidebar.button("Start Breathing")
    stop_button = st.sidebar.button("Stop")
    
    # Main visualization area
    st.subheader("Breathing Visualization")
    
    # Create placeholder for visualization
    viz_placeholder = st.empty()
    instruction_placeholder = st.empty()
    
    # Session state to track if animation is running
    if 'running' not in st.session_state:
        st.session_state.running = False
    
    if start_button:
        st.session_state.running = True
    
    if stop_button:
        st.session_state.running = False
    
    # Run the breathing animation if started
    if st.session_state.running:
        run_breathing_animation(
            viz_placeholder, 
            instruction_placeholder,
            inhale_time, 
            exhale_time, 
            hold_time,
            viz_style
        )

def run_breathing_animation(viz_placeholder, instruction_placeholder, inhale_time, exhale_time, hold_time, viz_style):
    """Run the breathing animation loop"""
    try:
        while st.session_state.running:
            # Inhale phase
            instruction_placeholder.markdown("## Inhale")
            steps = 20  # Number of animation steps
            
            for i in range(steps + 1):
                progress = i / steps
                fig = create_visualization(progress, viz_style, "inhale")
                viz_placeholder.pyplot(fig)
                plt.close(fig)
                time.sleep(inhale_time / steps)
                
                if not st.session_state.running:
                    break
            
            if not st.session_state.running:
                break
                
            # Hold phase (if any)
            if hold_time > 0:
                instruction_placeholder.markdown("## Hold")
                hold_start = time.time()
                while time.time() - hold_start < hold_time:
                    if not st.session_state.running:
                        break
                    time.sleep(0.1)
            
            if not st.session_state.running:
                break
                
            # Exhale phase
            instruction_placeholder.markdown("## Exhale")
            for i in range(steps + 1):
                progress = 1 - (i / steps)
                fig = create_visualization(progress, viz_style, "exhale")
                viz_placeholder.pyplot(fig)
                plt.close(fig)
                time.sleep(exhale_time / steps)
                
                if not st.session_state.running:
                    break
    
    except Exception as e:
        st.error(f"Animation error: {e}")
        st.session_state.running = False

def create_visualization(progress, style, phase):
    """Create the breathing visualization based on the selected style"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if style == "Circle":
        # Create a circle that grows/shrinks with breathing
        size = 0.1 + progress * 0.8  # Scale from 10% to 90% of max size
        circle = plt.Circle((0.5, 0.5), size/2, color='skyblue', alpha=0.7)
        ax.add_patch(circle)
        
        # Add a reference circle
        ref_circle = plt.Circle((0.5, 0.5), 0.45, fill=False, color='gray', linestyle='--', alpha=0.5)
        ax.add_patch(ref_circle)
        
    elif style == "Lung":
        # Create a lung-like shape
        x = np.linspace(0, 1, 100)
        y1 = 0.5 + 0.2 * np.sin(np.pi * x) * progress
        y2 = 0.5 - 0.2 * np.sin(np.pi * x) * progress
        
        ax.fill_between(x, y1, y2, color='pink', alpha=0.7)
        ax.plot(x, y1, color='red', alpha=0.8)
        ax.plot(x, y2, color='red', alpha=0.8)
        
    elif style == "Wave":
        # Create a wave that represents breathing
        x = np.linspace(0, 2*np.pi, 100)
        amplitude = progress * 0.4
        y = 0.5 + amplitude * np.sin(x)
        
        ax.plot(x, y, color='blue', linewidth=3)
        ax.fill_between(x, 0.5, y, color='lightblue', alpha=0.7)
    
    # Set the color based on the phase
    phase_color = 'skyblue' if phase == 'inhale' else 'lightgreen'
    
    # Add progress text
    ax.text(0.5, 0.05, f"{int(progress * 100)}%", 
            horizontalalignment='center', 
            verticalalignment='center',
            fontsize=16,
            color='black')
    
    # Configure the axes
    ax.set_xlim(0, 1 if style == "Circle" else (2*np.pi if style == "Wave" else 1))
    ax.set_ylim(0, 1)
    ax.set_aspect('equal' if style == "Circle" else 'auto')
    ax.axis('off')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    create_breathing_app()
