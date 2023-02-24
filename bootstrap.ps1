function Install-pytenable {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        $AccessKey,
        [Parameter(Mandatory=$true)]
        $SecretKey
    )
    
    begin {
        pip install pytenable
    }
    
    process {
        setx.exe TIO_ACCESS_KEY $AccessKey
        setx.exe TIO_SECRET_KEY $SecretKey
        "Restart terminal after to access env vars"
        Pause
    }
    
    end {
        
    }
}

