"""
recommender.py - Recommendation engine for skill gap system.
Maps missing skills to relevant courses from the SQLite database.
"""

import logging
from database import get_courses_for_skill

logger = logging.getLogger(__name__)


def get_recommendations(missing_skills: list[str]) -> list[dict]:
    """
    For each missing skill, fetch recommended courses from the database.
    
    Args:
        missing_skills: List of skills the user is missing for the job role.
    
    Returns:
        List of recommendation dicts, each containing:
        - skill: The missing skill name
        - courses: List of course dicts {course_name, course_url, platform}
    """
    recommendations = []

    for skill in missing_skills:
        courses = get_courses_for_skill(skill)
        if courses:
            recommendations.append({
                "skill": skill,
                "courses": courses
            })
            logger.info(f"[Recommender] Found {len(courses)} course(s) for skill: '{skill}'")
        else:
            # Still include the skill even if no courses are mapped
            recommendations.append({
                "skill": skill,
                "courses": [
                    {
                        "course_name": f"Search '{skill}' courses on Coursera",
                        "course_url": f"https://www.coursera.org/search?query={skill.replace(' ', '+')}",
                        "platform": "Coursera"
                    },
                    {
                        "course_name": f"Search '{skill}' courses on Udemy",
                        "course_url": f"https://www.udemy.com/courses/search/?q={skill.replace(' ', '+')}",
                        "platform": "Udemy"
                    }
                ]
            })
            logger.info(f"[Recommender] No direct mapping for '{skill}'; generated search links.")

    return recommendations
