/**
 * Retrieves the current authenticated user's profile.
 */
export const getProfile = async (req, res) => {
  try {
    const { data: profile, error } = await req.supabase
      .from('profiles')
      .select('id, display_name, created_at, updated_at')
      .eq('id', req.user.id)
      .maybeSingle();

    if (error) {
      console.error('Error fetching profile:', error.message);
      return res.status(500).json({
        error: {
          code: 'DATABASE_ERROR',
          message: 'Failed to fetch user profile',
        },
      });
    }

    if (!profile) {
      return res.status(404).json({
        error: {
          code: 'PROFILE_NOT_FOUND',
          message: 'User profile does not exist',
        },
      });
    }

    return res.status(200).json({ profile });
  } catch (err) {
    console.error('Unexpected error in getProfile:', err.message);
    return res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An unexpected error occurred while fetching profile',
      },
    });
  }
};

/**
 * Updates the current authenticated user's profile.
 * Strictly uses req.user.id and never trusts body for user identity.
 */
export const updateProfile = async (req, res) => {
  const { display_name } = req.body;

  try {
    const { data: updatedProfile, error } = await req.supabase
      .from('profiles')
      .update({
        display_name,
        updated_at: new Date().toISOString(),
      })
      .eq('id', req.user.id)
      .select('id, display_name, created_at, updated_at')
      .single();

    if (error) {
      console.error('Error updating profile:', error.message);
      return res.status(500).json({
        error: {
          code: 'DATABASE_ERROR',
          message: 'Failed to update user profile',
        },
      });
    }

    return res.status(200).json({ profile: updatedProfile });
  } catch (err) {
    console.error('Unexpected error in updateProfile:', err.message);
    return res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An unexpected error occurred while updating profile',
      },
    });
  }
};

