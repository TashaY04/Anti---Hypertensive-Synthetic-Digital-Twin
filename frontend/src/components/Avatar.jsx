import React from 'react';
import './Avatar.css';

const Avatar = ({ gender, recommendations }) => {
  const isMale = gender === 'male';
  const topDrug = recommendations?.[0]?.drug_name || '';
  
  return (
    <div className="avatar-container">
      <svg 
        width="200" 
        height="300" 
        viewBox="0 0 200 300" 
        className="avatar-svg"
      >
        {/* Head */}
        <circle cx="100" cy="60" r="35" fill={isMale ? "#FFD4A3" : "#FDE7D6"} stroke="#8B4513" strokeWidth="2"/>
        
        {/* Hair */}
        {isMale ? (
          <>
            <path d="M 70 40 Q 65 25 80 20 Q 100 15 120 20 Q 135 25 130 40" 
                  fill="#4A3728" />
            <path d="M 70 40 Q 68 55 75 65" fill="#4A3728" />
            <path d="M 130 40 Q 132 55 125 65" fill="#4A3728" />
          </>
        ) : (
          <>
            {/* Straight hair: rounded trapezoid + soft rectangle + U-shape */}
            <path
              d="M 70 40 Q 76 24 100 21 Q 124 24 130 40 L 126 53 Q 100 49 74 53 Z"
              fill="#2C1810"
            />
            <rect x="76" y="36" width="48" height="12" rx="6" fill="#2C1810" />
            <path
              d="M 72 46 Q 62 66 68 86 Q 84 94 100 94 Q 116 94 132 86 Q 138 66 128 46"
              stroke="#2C1810"
              strokeWidth="9"
              fill="none"
              strokeLinecap="round"
            />
          </>
        )}
        
        {/* Face */}
        {isMale ? (
          <>
            <circle cx="85" cy="60" r="4" fill="#000" />
            <circle cx="115" cy="60" r="4" fill="#000" />
            <path d="M 85 70 Q 100 78 115 70" stroke="#8B4513" strokeWidth="2" fill="none" />
          </>
        ) : (
          <>
            {/* Eyebrows */}
            <path d="M 78 54 Q 85 51 92 54" stroke="#3A2419" strokeWidth="1.6" fill="none" strokeLinecap="round" />
            <path d="M 108 54 Q 115 51 122 54" stroke="#3A2419" strokeWidth="1.6" fill="none" strokeLinecap="round" />
            {/* Eyes */}
            <circle cx="85" cy="61" r="3.6" fill="#111827" />
            <circle cx="115" cy="61" r="3.6" fill="#111827" />
            {/* Nose */}
            <path d="M 100 63 Q 98 67 100 70 Q 102 67 100 63" fill="none" stroke="#C38C6C" strokeWidth="1" />
            {/* Lips */}
            <path d="M 91 76 Q 100 81 109 76" stroke="#BE185D" strokeWidth="1.8" fill="none" strokeLinecap="round" />
          </>
        )}
        
        {/* Body */}
        {!isMale && (
          <>
            {/* Neck bridge so face connects naturally to body */}
            <rect x="92" y="88" width="16" height="14" rx="6" fill="#FDE7D6" stroke="#C38C6C" strokeWidth="1" />
          </>
        )}

        <rect x="75" y="95" width="50" height="80" rx="15" 
              fill={isMale ? "#4A90E2" : "#E91E63"} />

        {!isMale && (
          <>
            {/* Female neckline accent */}
            <path d="M 84 96 Q 100 114 116 96" stroke="#FBCFE8" strokeWidth="3" fill="none" />
          </>
        )}
        
        {/* Arms */}
        <rect x="45" y="105" width="30" height="12" rx="6" 
              fill={isMale ? "#FFD4A3" : "#FFE4C4"} />
        <rect x="125" y="105" width="30" height="12" rx="6" 
              fill={isMale ? "#FFD4A3" : "#FFE4C4"} />
        
        {/* Hands */}
        <circle cx="45" cy="111" r="8" fill={isMale ? "#FFD4A3" : "#FFE4C4"} />
        <circle cx="155" cy="111" r="8" fill={isMale ? "#FFD4A3" : "#FFE4C4"} />
        
        {/* Legs */}
        <rect x="80" y="175" width="18" height="70" rx="8" 
              fill={isMale ? "#2C3E50" : "#9C27B0"} />
        <rect x="102" y="175" width="18" height="70" rx="8" 
              fill={isMale ? "#2C3E50" : "#9C27B0"} />
        
        {/* Shoes */}
        <ellipse cx="89" cy="250" rx="12" ry="6" fill="#34495E" />
        <ellipse cx="111" cy="250" rx="12" ry="6" fill="#34495E" />
        
        {/* Medical Symbol */}
        <g transform="translate(95, 130)">
          <circle cx="5" cy="5" r="12" fill="#FFF" opacity="0.9"/>
          <rect x="2" y="-2" width="6" height="14" fill="#E74C3C" rx="1"/>
          <rect x="-2" y="2" width="14" height="6" fill="#E74C3C" rx="1"/>
        </g>
      </svg>
      
      <div className="avatar-info">
        <div className="avatar-badge">
          {isMale ? 'Male' : 'Female'} Patient
        </div>
        {topDrug && (
          <div className="avatar-treatment">
            {topDrug}
          </div>
        )}
      </div>
    </div>
  );
};

export default Avatar;
