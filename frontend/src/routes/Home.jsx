import { Box, Paper, Button, TextField, Typography } from '@mui/material';
import { useState, useRef } from 'react';
import axios from 'axios';
import { useEffect } from 'react';

import PoseEstimation from '../components/PoseEstimation';
export default function Home() {
    const ref = useRef(null);
    const [link, setLink] = useState("");

    const onSubmit = () => {
        console.log(link);
    }

    const handleSubmit = () => {
        if (!link) {
            return;
        }
        if (ref.current) {
            ref.current.requestSubmit();
        }
        setLink("");
    }

    useEffect(() => {
        const func = async () => {
            const res = await axios.get(import.meta.env.VITE_BASE_URL);
            console.log(res.data);
        }
        func();
    }, []);

    return (
        <div>
            <PoseEstimation />
            {/* <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                flexDirection="column"
                padding="10%"
            >
                <Paper
                    elevation={3}
                    sx={{
                        padding: 3,
                        borderRadius: 2,
                        backgroundColor: "white",
                        width: "100%",
                        maxWidth: 400,
                        boxShadow: 3,
                    }}>
                    <div>
                        <Typography variant="h5" gutterBottom align="center">
                            Enter a youtube link
                        </Typography>
                        <form
                            ref={ref}
                            onSubmit={(e) => {
                                e.preventDefault();
                                onSubmit();
                            }}>
                            <TextField
                                label="Youtube link"
                                variant="outlined"
                                margin="normal"
                                fullWidth
                                value={link}
                                onChange={(e) => setLink(e.target.value)}
                            />
                            <Box display="flex" justifyContent="center" mt={2}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    onClick={handleSubmit}
                                    sx={{ width: "100%" }}
                                >
                                    Submit
                                </Button>
                            </Box>
                        </form>
                    </div>
                </Paper>
            </Box> */}
        </div>
    );
}