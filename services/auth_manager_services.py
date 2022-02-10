

def CreateUnverifiedUserProfile(serializer):
    userProfile = serializer.create(serializer.validated_data)
    return userProfile.save()